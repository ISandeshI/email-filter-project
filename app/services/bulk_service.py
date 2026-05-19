from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone
from app.database.models import MasterContact


def bulk_upsert_master_contacts(db, df):

    if df.empty:
        return 0

    now = datetime.now(timezone.utc)

    df = df.copy()

    # normalize emails
    df["Email"] = df["Email"].astype(str).str.strip().str.lower()

    records = df[["First Name", "Last Name", "Email"]].to_dict(orient="records")

    formatted_records = []

    for r in records:
        formatted_records.append({
            "first_name": r.get("First Name"),
            "last_name": r.get("Last Name"),
            "email": r.get("Email"),

            # IMPORTANT:
            # store only FIRST time seen
            "first_uploaded_at": now
        })

    BATCH_SIZE = 20000

    for i in range(0, len(formatted_records), BATCH_SIZE):

        batch = formatted_records[i:i + BATCH_SIZE]

        stmt = insert(MasterContact).values(batch)

        stmt = stmt.on_conflict_do_update(
            index_elements=["email"],
            set_={
                "first_name": insert(MasterContact).excluded.first_name,
                "last_name": insert(MasterContact).excluded.last_name
                # ❌ DO NOT update first_uploaded_at
            }
        )

        db.execute(stmt)

    db.commit()

    return len(formatted_records)