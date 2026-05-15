from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import time
import pandas as pd
import uuid
import logging
from app.services.filter_service import process_file
from app.services.db_service import save_upload_history
from app.services.bulk_service import bulk_upsert_master_contacts

from app.database.connection import SessionLocal


router = APIRouter()
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["First Name", "Last Name", "Email"]
MAX_FILE_SIZE_MB = 25


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    start_time = time.time()

    # =========================
    # FILE SIZE VALIDATION
    # =========================

    file.file.seek(0, 2)

    file_size = file.file.tell()

    file.file.seek(0)

    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return {
            "error": f"File size exceeds {MAX_FILE_SIZE_MB}MB limit"
        }

    # =========================
    # OUTPUT FILE SETUP
    # =========================

    filtered_output_path = (
        f"filtered_files/filtered_{uuid.uuid4().hex}.xlsx"
    )

    excel_writer = pd.ExcelWriter(
        filtered_output_path,
        engine="openpyxl"
    )

    sheet_row = 0

    original_rows = 0
    total_valid_rows = 0
    total_removed_duplicates = 0
    total_removed_invalid = 0
    total_removed_unsubscribed = 0
    total_removed_recent = 0

    # =========================
    # XLSX PROCESSING
    # =========================

    if file.filename.endswith(".xlsx"):

        df = pd.read_excel(file.file)

        missing_columns = [
            col for col in REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing_columns:
            return {
                "error": "Missing required columns",
                "missing_columns": missing_columns
            }

        original_rows = len(df)

        db = SessionLocal()

        try:

            processing_time = int(time.time() - start_time)

            save_upload_history(
                db,
                file.filename,
                original_rows,
                total_valid_rows,
                processing_time
            )

        except Exception as e:

            db.rollback()

            logger.exception("Upload processing failed")

            return {
                "error": "Internal server error"
            }

        finally:
            db.close()

        if sheet_row == 0:

            pd.DataFrame(columns=REQUIRED_COLUMNS).to_excel(
                excel_writer,
                index=False
            )

        excel_writer.close()

    # =========================
    # CSV PROCESSING
    # =========================

    elif file.filename.endswith(".csv"):

        chunk_iterator = pd.read_csv(
            file.file,
            chunksize=20000
        )

        db = SessionLocal()

        try:

            for chunk in chunk_iterator:

                missing_columns = [
                    col for col in REQUIRED_COLUMNS
                    if col not in chunk.columns
                ]

                if missing_columns:
                    return {
                        "error": "Missing required columns",
                        "missing_columns": missing_columns
                    }

                original_rows += len(chunk)

                result = process_file(chunk, db)

                filtered_chunk = result["filtered_df"]

                stats = result["stats"]

                total_removed_duplicates += (
                    stats["removed_duplicates"]
                )

                total_removed_invalid += (
                    stats["removed_invalid"]
                )

                total_removed_unsubscribed += (
                    stats["removed_unsubscribed"]
                )

                total_removed_recent += (
                    stats["removed_recent"]
                )

                if not filtered_chunk.empty:
                    bulk_upsert_master_contacts(db, filtered_chunk)

                if not filtered_chunk.empty:

                    total_valid_rows += stats["valid_rows"]

                    filtered_chunk.to_excel(
                        excel_writer,
                        index=False,
                        header=(sheet_row == 0),
                        startrow=sheet_row
                    )

                    sheet_row += len(filtered_chunk)

        finally:
            db.close()

        if sheet_row == 0:

            pd.DataFrame(columns=REQUIRED_COLUMNS).to_excel(
                excel_writer,
                index=False
            )

        excel_writer.close()

    else:
        return {
            "error": "Only .xlsx and .csv files are supported"
        }

    # =========================
    # SAVE UPLOAD HISTORY
    # =========================

    db = SessionLocal()

    try:

        processing_time = int(time.time() - start_time)

        save_upload_history(
            db,
            file.filename,
            original_rows,
            total_valid_rows,
            processing_time
        )

    finally:
        db.close()

    # =========================
    # RETURN FILE
    # =========================

    return JSONResponse({

        "success": True,

        "download_url": (
            f"http://127.0.0.1:8000/download/"
            f"{filtered_output_path.split('/')[-1]}"
        ),

        "stats": {

            "original_rows": original_rows,

            "valid_rows": total_valid_rows,

            "removed_rows": (
                original_rows - total_valid_rows
            ),

            "removed_duplicates":
                total_removed_duplicates,

            "removed_invalid":
                total_removed_invalid,

            "removed_unsubscribed":
                total_removed_unsubscribed,

            "removed_recent":
                total_removed_recent,

            "processing_time_seconds":
                int(time.time() - start_time)
        }
    })

@router.get("/download/{filename}")
async def download_file(filename: str):

    return FileResponse(
        path=f"filtered_files/{filename}",
        filename="filtered_contacts.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )