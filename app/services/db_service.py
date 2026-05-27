from datetime import datetime, timezone

from app.database.models import (
    MasterContact,
    UploadHistory
)


def save_upload_history(
    db,
    upload_id,
    filename,
    total_rows,
    valid_rows,
    processing_time,
    removed_duplicates=0,
    removed_invalid=0,
    removed_unsubscribed=0,
    removed_recent=0
):

    record = UploadHistory(

        upload_id=upload_id,

        filename=filename,

        total_rows=total_rows,

        valid_rows=valid_rows,

        removed_duplicates=removed_duplicates,

        removed_invalid=removed_invalid,

        removed_unsubscribed=removed_unsubscribed,

        removed_recent=removed_recent,

        processing_time_seconds=processing_time
    )

    db.add(record)

    db.commit()


def upsert_master_contacts(db, df):

    now = datetime.now(timezone.utc)

    for _, row in df.iterrows():

        email = row["Email"]

        existing = db.query(MasterContact).filter(
            MasterContact.email == email
        ).first()

        if existing:

            existing.last_used_at = now

        else:

            db.add(
                MasterContact(
                    first_name=row.get("First Name"),
                    last_name=row.get("Last Name"),
                    email=email,
                    first_uploaded_at=now,
                    last_used_at=now
                )
            )

    db.commit()