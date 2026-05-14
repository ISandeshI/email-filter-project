from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

from app.database.connection import Base


class MasterContact(Base):
    __tablename__ = "master_contacts"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String)
    last_name = Column(String)

    email = Column(String, unique=True, index=True)

    first_uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    last_used_at = Column(DateTime, index=True, nullable=True)


class UnsubscribedContact(Base):
    __tablename__ = "unsubscribed_contacts"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True)

    unsubscribed_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    reason = Column(String, nullable=True)


class UploadHistory(Base):
    __tablename__ = "upload_history"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String)

    uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    total_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)

    removed_duplicates = Column(Integer, default=0)
    removed_invalid = Column(Integer, default=0)
    removed_unsubscribed = Column(Integer, default=0)
    removed_recent = Column(Integer, default=0)

    processing_time_seconds = Column(Integer, default=0)


class TempUploadContact(Base):
    __tablename__ = "temp_upload_contacts"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String)
    last_name = Column(String)

    email = Column(String, index=True)

    upload_batch = Column(String, index=True)