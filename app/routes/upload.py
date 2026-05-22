from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import time
import redis
import json
import pandas as pd

from app.services.filter_service import process_upload_task
from app.database.connection import SessionLocal
from app.database.models import CampaignSnapshot, UnsubscribedContact, BouncedContact

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = f"{UPLOAD_DIR}/{uuid.uuid4().hex}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    upload_id = int(time.time())

    process_upload_task.delay(file_path, upload_id)

    return JSONResponse({
        "success": True,
        "message": "File is being processed in background",
        "upload_id": upload_id
    })


@router.get("/download/{upload_id}")
async def download_file(upload_id: int):

    db = SessionLocal()

    try:

        snapshot = db.query(CampaignSnapshot).filter(
            CampaignSnapshot.upload_id == upload_id
        ).all()

        if not snapshot:

            empty_path = f"filtered_files/empty_{upload_id}.csv"

            pd.DataFrame(
                columns=["First Name", "Last Name", "Email"]
            ).to_csv(empty_path, index=False)

            return FileResponse(
                path=empty_path,
                filename=f"filtered_{upload_id}.csv",
                media_type="text/csv"
            )

        emails = [s.email for s in snapshot]

        # latest unsubscribed list
        unsubscribed = set(
            r[0] for r in db.query(
                UnsubscribedContact.email
            ).filter(
                UnsubscribedContact.email.in_(emails)
            ).all()
        )

        # latest bounced list
        bounced = set(
            r[0] for r in db.query(
                BouncedContact.email
            ).filter(
                BouncedContact.email.in_(emails)
            ).all()
        )

        final_rows = []

        for row in snapshot:

            if (
                row.email not in unsubscribed
                and row.email not in bounced
            ):

                final_rows.append({
                    "First Name": row.first_name,
                    "Last Name": row.last_name,
                    "Email": row.email
                })

        if not final_rows:
            return {"error": "No valid contacts remaining"}

        os.makedirs("filtered_files", exist_ok=True)

        refreshed_file = (
            f"filtered_files/refreshed_{upload_id}.csv"
        )

        df = pd.DataFrame(final_rows)

        df.to_csv(refreshed_file, index=False)

        return FileResponse(
            path=refreshed_file,
            filename=f"filtered_{upload_id}.csv",
            media_type="text/csv"
        )

    finally:
        db.close()


@router.get("/upload/status/{upload_id}")
async def get_upload_status(upload_id: int):

    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    data = redis_client.get(f"upload:{upload_id}")

    if not data:
        return {"status": "not_found"}

    return json.loads(data)