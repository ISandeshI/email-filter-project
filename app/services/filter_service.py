import re
from sqlalchemy import delete
from app.database.models import TempUploadContact
from app.services.staging_service import stage_uploaded_contacts
from sqlalchemy import select

from app.database.models import (
    UnsubscribedContact,
    MasterContact
)

from datetime import datetime, timedelta, timezone


EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


def process_file(df, db):

    # Normalize emails
    df["Email"] = (
        df["Email"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Remove blank emails
    df = df[df["Email"] != ""]

    # Remove duplicates
    df = df.drop_duplicates(subset=["Email"])

    # Regex validation
    valid_df = df[
        df["Email"].apply(
            lambda x: bool(EMAIL_REGEX.match(x))
        )
    ]

    if valid_df.empty:
        return valid_df

    # =========================
    # STAGE DATA
    # =========================

    batch_id = stage_uploaded_contacts(db, valid_df)

    # =========================
    # UNSUBSCRIBED FILTER
    # =========================

    unsubscribed_emails = set(

        db.execute(

            select(TempUploadContact.email)
            .join(
                UnsubscribedContact,
                TempUploadContact.email == UnsubscribedContact.email
            )
            .where(
                TempUploadContact.upload_batch == batch_id
            )

        ).scalars().all()

    )

    filtered_df = valid_df[
        ~valid_df["Email"].isin(unsubscribed_emails)
    ]

    # =========================
    # RECENT FILTER
    # =========================

    ninety_days_ago = (
        datetime.now(timezone.utc)
        - timedelta(days=90)
    )

    recent_emails = set(

        db.execute(

            select(TempUploadContact.email)
            .join(
                MasterContact,
                TempUploadContact.email == MasterContact.email
            )
            .where(
                TempUploadContact.upload_batch == batch_id,
                MasterContact.last_used_at >= ninety_days_ago
            )

        ).scalars().all()

    )

    filtered_df = filtered_df[
        ~filtered_df["Email"].isin(recent_emails)
    ]

    # =========================
    # CLEANUP STAGING
    # =========================

    db.execute(
        delete(TempUploadContact).where(
            TempUploadContact.upload_batch == batch_id
        )
    )

    db.commit()

    return filtered_df