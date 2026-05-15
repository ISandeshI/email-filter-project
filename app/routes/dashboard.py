from fastapi import APIRouter
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.database.connection import SessionLocal
from app.database.models import (
    MasterContact,
    UnsubscribedContact,
    UploadHistory
)

router = APIRouter()


@router.get("/dashboard/stats")
def dashboard_stats():

    db = SessionLocal()

    try:

        ninety_days_ago = (
            datetime.now(timezone.utc)
            - timedelta(days=90)
        )

        total_master_contacts = db.query(
            func.count(MasterContact.id)
        ).scalar()

        total_unsubscribed = db.query(
            func.count(UnsubscribedContact.id)
        ).scalar()

        used_last_90_days = db.query(
            func.count(MasterContact.id)
        ).filter(
            MasterContact.last_used_at >= ninety_days_ago
        ).scalar()

        total_uploads = db.query(
            func.count(UploadHistory.id)
        ).scalar()

        total_filtered_contacts = db.query(
            func.sum(UploadHistory.valid_rows)
        ).scalar()

        return {
            "total_master_contacts": total_master_contacts or 0,
            "total_unsubscribed": total_unsubscribed or 0,
            "used_last_90_days": used_last_90_days or 0,
            "total_uploads": total_uploads or 0,
            "total_filtered_contacts": total_filtered_contacts or 0
        }

    finally:
        db.close()