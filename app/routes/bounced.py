from fastapi import APIRouter, UploadFile, File
import pandas as pd

from app.database.connection import SessionLocal
from app.database.models import BouncedContact

router = APIRouter()

REQUIRED_COLUMNS = ["Email"]


@router.post("/upload/bounced")
async def upload_bounced(file: UploadFile = File(...)):

    if not (
        file.filename.endswith(".csv") or file.filename.endswith(".xlsx")
    ):
        return {"error": "Only CSV/XLSX supported"}

    df = pd.read_csv(file.file) if file.filename.endswith(".csv") else pd.read_excel(file.file)

    if "Email" not in df.columns:
        return {"error": "Email column required"}

    df["Email"] = (
        df["Email"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df = df[df["Email"] != ""]
    df = df.drop_duplicates(subset=["Email"])

    db = SessionLocal()
    inserted = 0

    try:

        existing = set(
            r[0] for r in db.query(BouncedContact.email).all()
        )

        for email in df["Email"]:
            if email not in existing:
                db.add(BouncedContact(email=email))
                inserted += 1

        db.commit()

        return {
            "success": True,
            "total_uploaded": len(df),
            "inserted": inserted
        }

    finally:
        db.close()