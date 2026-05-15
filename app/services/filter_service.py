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

    original_rows = len(df)

    # =========================
    # NORMALIZE
    # =========================

    df["Email"] = (
        df["Email"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # =========================
    # REMOVE BLANK EMAILS
    # =========================

    df = df[df["Email"] != ""]

    # =========================
    # REMOVE DUPLICATES
    # =========================

    before_duplicates = len(df)

    df = df.drop_duplicates(subset=["Email"])

    removed_duplicates = (
        before_duplicates - len(df)
    )

    # =========================
    # REGEX VALIDATION
    # =========================

    before_validation = len(df)

    valid_df = df[
        df["Email"].apply(
            lambda x: bool(EMAIL_REGEX.match(x))
        )
    ]

    removed_invalid = (
        before_validation - len(valid_df)
    )

    if valid_df.empty:

        return {
            "filtered_df": valid_df,
            "stats": {
                "original_rows": original_rows,
                "valid_rows": 0,
                "removed_duplicates": removed_duplicates,
                "removed_invalid": removed_invalid,
                "removed_unsubscribed": 0,
                "removed_recent": 0
            }
        }

    # =========================
    # STAGE DATA
    # =========================

    batch_id = stage_uploaded_contacts(
        db,
        valid_df
    )

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

    removed_unsubscribed = len(
        unsubscribed_emails
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

    removed_recent = len(
        recent_emails
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

    return {
        "filtered_df": filtered_df,
        "stats": {
            "original_rows": original_rows,
            "valid_rows": len(filtered_df),
            "removed_duplicates": removed_duplicates,
            "removed_invalid": removed_invalid,
            "removed_unsubscribed": removed_unsubscribed,
            "removed_recent": removed_recent
        }
    }