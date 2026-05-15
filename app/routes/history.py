from fastapi import APIRouter

from app.database.connection import SessionLocal
from app.database.models import UploadHistory

router = APIRouter()


@router.get("/upload/history")
def upload_history():

    db = SessionLocal()

    try:

        history = db.query(
            UploadHistory
        ).order_by(
            UploadHistory.uploaded_at.desc()
        ).limit(50).all()

        results = []

        for item in history:

            results.append({
                "filename": item.filename,
                "uploaded_at": item.uploaded_at,
                "total_rows": item.total_rows,
                "valid_rows": item.valid_rows,
                "processing_time_seconds": item.processing_time_seconds
            })

        return {
            "results": results
        }

    finally:
        db.close()