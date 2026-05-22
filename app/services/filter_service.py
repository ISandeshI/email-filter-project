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
from app.database.models import CampaignSnapshot


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

            filtered_df.to_csv(
                filtered_output_path,
                index=False
            )

            output_created = True

        # =========================
        # CSV PROCESSING
        # =========================

        else:

            chunk_iterator = pd.read_csv(
                file_path,
                chunksize=20000
            )

            first_chunk = True

            filtered_df_list = []

            for chunk in chunk_iterator:

                original_rows += len(chunk)

                result = process_file(chunk, db)

                filtered_chunk = result["filtered_df"]

                stats = result["stats"]

                total_valid_rows += stats["valid_rows"]

                filtered_df_list.append(filtered_chunk)

                filtered_chunk.to_csv(
                    filtered_output_path,
                    mode="a" if output_created else "w",
                    index=False,
                    header=first_chunk
                )

                output_created = True
                first_chunk = False

            filtered_df = pd.concat(filtered_df_list) if filtered_df_list else pd.DataFrame()

        # =========================
        # MASTER UPLOAD LOGIC
        # =========================

        # =========================
        # SNAPSHOT INSERT (FIXED + SAFE)
        # =========================

        # clean old snapshot
        db.query(CampaignSnapshot).filter(
            CampaignSnapshot.upload_id == upload_id
        ).delete()

        snapshot_rows = filtered_df.to_dict(orient="records")

        snapshot_objects = [
            CampaignSnapshot(
                upload_id=upload_id,
                email=r.get("Email"),
                first_name=r.get("First Name"),
                last_name=r.get("Last Name")
            )
            for r in snapshot_rows
        ]

        if snapshot_objects:
            db.bulk_save_objects(snapshot_objects)

        if not filtered_df.empty:
            bulk_upsert_master_contacts(db, filtered_df)

        db.commit()

        processing_time = int(time.time() - start_time)

        save_upload_history(
            db,
            upload_id,
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