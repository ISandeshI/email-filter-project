import pandas as pd
import time
import redis
import json
import os

from app.database.connection import SessionLocal
from app.services.db_service import save_upload_history
from app.services.bulk_service import bulk_upsert_master_contacts
from app.core.filter_engine import process_file
from app.celery_worker import celery


@celery.task
def process_upload_task(file_path: str, upload_id: int):

    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        db=0
    )

    redis_key = f"upload:{upload_id}"

    start_time = time.time()

    original_rows = 0
    total_valid_rows = 0

    os.makedirs("filtered_files", exist_ok=True)

    filtered_output_path = (
        f"filtered_files/filtered_{upload_id}.csv"
    )

    db = SessionLocal()

    try:

        redis_client.set(
            redis_key,
            json.dumps({
                "status": "processing",
                "progress": 10
            })
        )

        output_created = False

        # =========================
        # XLSX PROCESSING
        # =========================

        if file_path.endswith(".xlsx"):

            df = pd.read_excel(file_path)

            original_rows = len(df)

            result = process_file(df, db)

            filtered_df = result["filtered_df"]

            stats = result["stats"]

            total_valid_rows = stats["valid_rows"]

            # Always create CSV
            filtered_df.to_csv(
                filtered_output_path,
                index=False
            )

            output_created = True

            if not filtered_df.empty:

                bulk_upsert_master_contacts(
                    db,
                    filtered_df
                )

        # =========================
        # CSV PROCESSING
        # =========================

        else:

            chunk_iterator = pd.read_csv(
                file_path,
                chunksize=20000
            )

            first_chunk = True

            for chunk in chunk_iterator:

                original_rows += len(chunk)

                result = process_file(chunk, db)

                filtered_chunk = result["filtered_df"]

                stats = result["stats"]

                total_valid_rows += stats["valid_rows"]

                # Always create file
                filtered_chunk.to_csv(
                    filtered_output_path,
                    mode="a" if output_created else "w",
                    index=False,
                    header=first_chunk
                )

                output_created = True

                first_chunk = False

                if not filtered_chunk.empty:

                    bulk_upsert_master_contacts(
                        db,
                        filtered_chunk
                    )

        processing_time = int(
            time.time() - start_time
        )

        save_upload_history(
            db,
            file_path.split("/")[-1],
            original_rows,
            total_valid_rows,
            processing_time
        )

        redis_client.set(
            redis_key,
            json.dumps({
                "status": "completed",
                "upload_id": upload_id,
                "original_rows": original_rows,
                "valid_rows": total_valid_rows,
                "processing_time": processing_time
            })
        )

        return {
            "upload_id": upload_id,
            "status": "completed"
        }

    except Exception as e:

        db.rollback()

        redis_client.set(
            redis_key,
            json.dumps({
                "status": "failed",
                "error": str(e)
            })
        )

        raise e

    finally:

        db.close()