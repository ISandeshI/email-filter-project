from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
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

                filtered_chunk = process_file(chunk, db)
                if not filtered_chunk.empty:
                    bulk_upsert_master_contacts(db, filtered_chunk)

                if not filtered_chunk.empty:

                    total_valid_rows += len(filtered_chunk)

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

    return FileResponse(
        path=filtered_output_path,
        filename="filtered_contacts.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )