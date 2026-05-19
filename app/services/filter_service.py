import pandas as pd
import time
import redis
import json

from app.database.connection import SessionLocal
from app.services.db_service import save_upload_history
from app.services.bulk_service import bulk_upsert_master_contacts
from app.core.filter_engine import process_file
from app.celery_worker import celery


@celery.task
def process_upload_task(file_path: str, upload_id: int):

    redis_client = redis.Redis(host="localhost", port=6379, db=0)
    redis_key = f"upload:{upload_id}"

    start_time = time.time()

    original_rows = 0
    total_valid_rows = 0

    filtered_output_path = f"filtered_files/filtered_{upload_id}.xlsx"
    excel_writer = pd.ExcelWriter(filtered_output_path, engine="openpyxl")

    db = SessionLocal()

    try:

        redis_client.set(redis_key, json.dumps({
            "status": "processing",
            "progress": 10
        }))

        # =========================
        # XLSX PROCESSING
        # =========================
        if file_path.endswith(".xlsx"):

            df = pd.read_excel(file_path)
            original_rows = len(df)

            # IMPORT INSIDE TASK (important fix)
            from app.core.filter_engine import process_file

            result = process_file(df, db)

            filtered_df = result["filtered_df"]
            stats = result["stats"]

            total_valid_rows = stats["valid_rows"]

            filtered_df.to_excel(excel_writer, index=False)

            if not filtered_df.empty:
                bulk_upsert_master_contacts(db, filtered_df)

        # =========================
        # CSV PROCESSING
        # =========================
        else:

            chunk_iterator = pd.read_csv(file_path, chunksize=20000)
            sheet_row = 0

            for chunk in chunk_iterator:

                original_rows += len(chunk)

                # IMPORT INSIDE LOOP (important fix)
                from app.core.filter_engine import process_file

                result = process_file(chunk, db)

                filtered_chunk = result["filtered_df"]
                stats = result["stats"]

                total_valid_rows += stats["valid_rows"]

                if not filtered_chunk.empty:

                    bulk_upsert_master_contacts(db, filtered_chunk)

                    filtered_chunk.to_excel(
                        excel_writer,
                        index=False,
                        header=(sheet_row == 0),
                        startrow=sheet_row
                    )

                    sheet_row += len(filtered_chunk)

        excel_writer.close()

        processing_time = int(time.time() - start_time)

        save_upload_history(
            db,
            file_path.split("/")[-1],
            original_rows,
            total_valid_rows,
            processing_time
        )

        redis_client.set(redis_key, json.dumps({
            "status": "completed",
            "upload_id": upload_id,
            "original_rows": original_rows,
            "valid_rows": total_valid_rows,
            "processing_time": processing_time
        }))

        return {
            "upload_id": upload_id,
            "status": "completed"
        }

    except Exception as e:

        db.rollback()

        redis_client.set(redis_key, json.dumps({
            "status": "failed",
            "error": str(e)
        }))

        raise e

    finally:
        db.close()