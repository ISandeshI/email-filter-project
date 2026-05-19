from fastapi import APIRouter, Query

from app.database.connection import SessionLocal
from app.database.models import UploadHistory

router = APIRouter()


@router.get("/upload/history")
def upload_history(

    page: int = Query(1),

    limit: int = Query(10)

):

    db = SessionLocal()

    try:

        offset = (page - 1) * limit

        total_records = db.query(
            UploadHistory
        ).count()

        history = db.query(
            UploadHistory
        ).order_by(
            UploadHistory.uploaded_at.desc()
        ).offset(offset).limit(limit).all()

        results = []

        for item in history:

            results.append({
                "filename": item.filename,
                "uploaded_at": item.uploaded_at,
                "total_rows": item.total_rows,
                "valid_rows": item.valid_rows,
                "processing_time_seconds":
                    item.processing_time_seconds
            })

        return {
            "results": results,
            "page": page,
            "limit": limit,
            "total_records": total_records,
            "total_pages": (
                total_records + limit - 1
            ) // limit
        }

    finally:
        db.close()