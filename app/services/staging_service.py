import uuid

from sqlalchemy.dialects.postgresql import insert

from app.database.models import TempUploadContact


def stage_uploaded_contacts(db, df):

    batch_id = str(uuid.uuid4())

    records = df[
        ["First Name", "Last Name", "Email"]
    ].to_dict(orient="records")

    formatted_records = [
        {
            "first_name": r.get("First Name"),
            "last_name": r.get("Last Name"),
            "email": r.get("Email"),
            "upload_batch": batch_id
        }
        for r in records
    ]

    BATCH_SIZE = 20000

    for i in range(0, len(formatted_records), BATCH_SIZE):

        batch = formatted_records[i:i + BATCH_SIZE]

        stmt = insert(TempUploadContact).values(batch)

        db.execute(stmt)

    db.commit()

    return batch_id