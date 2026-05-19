from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import time
import redis
import json
from app.services.filter_service import process_upload_task

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    start_time = time.time()

    file_path = f"{UPLOAD_DIR}/{uuid.uuid4().hex}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    file.file.seek(0)

    upload_id = int(time.time())

    process_upload_task.delay(file_path, upload_id)

    return JSONResponse({
        "success": True,
        "message": "File is being processed in background",
        "upload_id": upload_id
    })


@router.get("/download/{filename}")
async def download_file(filename: str):

    file_path = f"filtered_files/{filename}"

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/upload/status/{upload_id}")
async def get_upload_status(upload_id: int):

    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    data = redis_client.get(f"upload:{upload_id}")

    if not data:
        return {
            "status": "not_found"
        }

    return json.loads(data)

