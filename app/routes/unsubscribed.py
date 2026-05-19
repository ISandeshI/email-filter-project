from fastapi import APIRouter, UploadFile, File
import pandas as pd

from app.database.connection import SessionLocal
from app.database.models import UnsubscribedContact

router = APIRouter()

REQUIRED_COLUMNS = ["Email"]


@router.post("/upload/unsubscribed")
async def upload_unsubscribed(
    file: UploadFile = File(...)
):

    if not (
        file.filename.endswith(".csv")
        or file.filename.endswith(".xlsx")
    ):
        return {
            "error": "Only CSV/XLSX supported"
        }

    # =========================
    # READ FILE
    # =========================

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)

    else:
        df = pd.read_excel(file.file)

    # =========================
    # VALIDATE COLUMNS
    # =========================

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        return {
            "error": "Missing required columns",
            "missing_columns": missing_columns
        }

    # =========================
    # NORMALIZE EMAILS
    # =========================

    df["Email"] = (
        df["Email"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df = df[df["Email"] != ""]

    df = df.drop_duplicates(
        subset=["Email"]
    )

    # =========================
    # SAVE TO DATABASE
    # =========================

    db = SessionLocal()

    inserted = 0

    try:

        existing_emails = set(

            row[0] for row in db.query(
                UnsubscribedContact.email
            ).all()

        )

        for email in df["Email"]:

            if email not in existing_emails:

                db.add(
                    UnsubscribedContact(
                        email=email
                    )
                )

                inserted += 1

        db.commit()

        return {
            "success": True,
            "total_uploaded": len(df),
            "inserted": inserted
        }

    finally:
        db.close()