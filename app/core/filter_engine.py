import re
import pandas as pd
from datetime import datetime, timedelta

from app.database.models import (
    UnsubscribedContact,
    MasterContact,
    BouncedContact
)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def is_valid_email(email: str) -> bool:
    if not isinstance(email, str):
        return False
    return re.match(EMAIL_REGEX, email.strip()) is not None


def process_file(df: pd.DataFrame, db):

    now = datetime.utcnow()
    cutoff_date = now - timedelta(days=90)

    df = df.copy()

    # -----------------------
    # Normalize email
    # -----------------------
    # normalize column names first
    df.columns = [c.strip() for c in df.columns]

    # find email column dynamically
    email_col = None
    for c in df.columns:
        if c.lower() == "email":
            email_col = c
            break

    if not email_col:
        raise ValueError("Email column not found in uploaded file")

    df["Email"] = df[email_col].astype(str).str.strip().str.lower()

    # -----------------------
    # VALID EMAIL FILTER
    # -----------------------
    valid_mask = df["Email"].apply(is_valid_email)
    invalid_removed = len(df) - valid_mask.sum()
    df = df[valid_mask]

    # -----------------------
    # DUPLICATE REMOVAL
    # -----------------------
    before_dup = len(df)
    df = df.drop_duplicates(subset=["Email"])
    dup_removed = before_dup - len(df)

    # -----------------------
    # INIT SAFE DEFAULTS
    # -----------------------
    recent_set = set()
    unsub_set = set()
    bounced_set = set()

    emails = df["Email"].tolist()

    if emails:

        recent_rows = db.query(MasterContact.email).filter(
            MasterContact.email.in_(emails),
            MasterContact.first_uploaded_at >= cutoff_date
        ).all()
        recent_set = {r[0] for r in recent_rows}

        unsub_rows = db.query(UnsubscribedContact.email).filter(
            UnsubscribedContact.email.in_(emails)
        ).all()
        unsub_set = {r[0] for r in unsub_rows}

        bounced_rows = db.query(BouncedContact.email).filter(
            BouncedContact.email.in_(emails)
        ).all()
        bounced_set = {r[0] for r in bounced_rows}

    # -----------------------
    # MERGE SUPPRESSIONS
    # -----------------------
    suppressed_set = recent_set.union(unsub_set).union(bounced_set)

    before_supp = len(df)
    df = df[~df["Email"].isin(suppressed_set)]
    suppressed_removed = before_supp - len(df)

    # -----------------------
    # FINAL OUTPUT
    # -----------------------
    stats = {
        "valid_rows": len(df),

        "removed_duplicates": dup_removed,
        "removed_invalid": invalid_removed,

        "removed_unsubscribed": len(unsub_set),
        "removed_bounced": len(bounced_set),
        "removed_recent": len(recent_set)
    }

    return {
        "filtered_df": df,
        "stats": stats
    }