from fastapi import APIRouter
from sqlalchemy import func, cast, Date
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

        total_duplicates_removed = db.query(
            func.sum(UploadHistory.removed_duplicates)
        ).scalar()

        total_invalid_removed = db.query(
            func.sum(UploadHistory.removed_invalid)
        ).scalar()

        total_unsubscribed_removed = db.query(
            func.sum(UploadHistory.removed_unsubscribed)
        ).scalar()

        total_recent_removed = db.query(
            func.sum(UploadHistory.removed_recent)
        ).scalar()

        return {
            "total_master_contacts": total_master_contacts or 0,
            "total_unsubscribed": total_unsubscribed or 0,
            "used_last_90_days": used_last_90_days or 0,
            "total_uploads": total_uploads or 0,
            "total_filtered_contacts": total_filtered_contacts or 0,

            "total_duplicates_removed":
                total_duplicates_removed or 0,

            "total_invalid_removed":
                total_invalid_removed or 0,

            "total_unsubscribed_removed":
                total_unsubscribed_removed or 0,

            "total_recent_removed":
                total_recent_removed or 0
        }

    finally:
        db.close()

@router.get("/dashboard/upload-trend")
def upload_trend():

    db = SessionLocal()

    try:

        trend_data = (
            db.query(
                cast(UploadHistory.uploaded_at, Date).label("date"),
                func.count(UploadHistory.id).label("uploads")
            )
            .group_by(
                cast(UploadHistory.uploaded_at, Date)
            )
            .order_by(
                cast(UploadHistory.uploaded_at, Date)
            )
            .all()
        )

        return [
            {
                "date": str(item.date),
                "uploads": item.uploads
            }
            for item in trend_data
        ]

    finally:
        db.close()