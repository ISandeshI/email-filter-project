from sqlalchemy.dialects.postgresql import insert
from app.database.models import MasterContact
from datetime import datetime, timezone


def bulk_upsert_master_contacts(db, df):

    if df.empty:
        return 0

    now = datetime.now(timezone.utc)

    # Normalize column access once (faster than repeated row.get)
    df = df.copy()

    df["Email"] = df["Email"].astype(str).str.strip().str.lower()

    records = df[["First Name", "Last Name", "Email"]].to_dict(orient="records")

    # Convert to DB format (faster than iterrows)
    formatted_records = [
        {
            "first_name": r.get("First Name"),
            "last_name": r.get("Last Name"),
            "email": r.get("Email"),
            "first_uploaded_at": now,
            "last_used_at": now
        }
        for r in records
    ]

    # Batch control (IMPORTANT for enterprise scale safety)
    BATCH_SIZE = 20000

    for i in range(0, len(formatted_records), BATCH_SIZE):

        batch = formatted_records[i:i + BATCH_SIZE]

        stmt = insert(MasterContact).values(batch)

        stmt = stmt.on_conflict_do_update(
            index_elements=["email"],
            set_={
                "last_used_at": now
            },
            where=(
                MasterContact.last_used_at.is_(None) |
                (MasterContact.last_used_at < now)
            )
        )

        db.execute(stmt)

    db.commit()

    return len(formatted_records)