from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone, timedelta

from app.database.models import MasterContact


def bulk_upsert_master_contacts(db, df):

    if df.empty:
        return 0

    now = datetime.now(timezone.utc)

    cutoff_date = now - timedelta(days=90)

    df = df.copy()

    # normalize emails
    df["Email"] = (
        df["Email"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    records = df[
        ["First Name", "Last Name", "Email"]
    ].to_dict(orient="records")

    emails = [
        r.get("Email")
        for r in records
    ]

    # -----------------------------
    # FETCH EXISTING CONTACTS
    # -----------------------------

    existing_contacts = db.query(
        MasterContact
    ).filter(
        MasterContact.email.in_(emails)
    ).all()

    existing_map = {
        c.email: c
        for c in existing_contacts
    }

    insert_records = []

    update_records = []

    # -----------------------------
    # APPLY BUSINESS LOGIC
    # -----------------------------

    for r in records:

        email = r.get("Email")

        existing = existing_map.get(email)

        # --------------------------------
        # NEW CONTACT
        # --------------------------------

        if not existing:

            insert_records.append({

                "first_name":
                    r.get("First Name"),

                "last_name":
                    r.get("Last Name"),

                "email":
                    email,

                "first_uploaded_at":
                    now,

                "last_used_at":
                    now
            })

        # --------------------------------
        # EXISTING CONTACT
        # --------------------------------

        else:

            # only refresh if older than 90 days
            if (
                existing.last_used_at is None
                or existing.last_used_at < cutoff_date
            ):

                update_records.append({

                    "id": existing.id,

                    "first_name":
                        r.get("First Name"),

                    "last_name":
                        r.get("Last Name"),

                    "last_used_at":
                        now
                })

    # -----------------------------
    # BULK INSERT NEW CONTACTS
    # -----------------------------

    if insert_records:

        stmt = insert(MasterContact).values(
            insert_records
        )

        db.execute(stmt)

    # -----------------------------
    # BULK UPDATE OLD CONTACTS
    # -----------------------------

    if update_records:

        for row in update_records:

            db.query(MasterContact).filter(
                MasterContact.id == row["id"]
            ).update({

                "first_name":
                    row["first_name"],

                "last_name":
                    row["last_name"],

                "last_used_at":
                    row["last_used_at"]
            })

    db.commit()

    return len(records)