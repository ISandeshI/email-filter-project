from fastapi import APIRouter, Query
from sqlalchemy import or_

from app.database.connection import SessionLocal
from app.database.models import (
    MasterContact,
    UnsubscribedContact
)

router = APIRouter()


@router.get("/contacts/search")
def search_contacts(

    email: str = Query(...),

    limit: int = 20

):

    db = SessionLocal()

    try:

        contacts = db.query(MasterContact).filter(
            MasterContact.email.ilike(f"%{email}%")
        ).limit(limit).all()

        results = []

        for contact in contacts:

            unsubscribed = db.query(
                UnsubscribedContact
            ).filter(
                UnsubscribedContact.email == contact.email
            ).first()

            results.append({
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "email": contact.email,
                "last_used_at": contact.last_used_at,
                "unsubscribed": bool(unsubscribed)
            })

        return {
            "results": results
        }

    finally:
        db.close()