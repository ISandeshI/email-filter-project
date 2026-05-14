from fastapi import FastAPI
from app.routes.upload import router as upload_router
from app.database.connection import engine
from app.database.models import Base

app = FastAPI()

# Create tables on startup
Base.metadata.create_all(bind=engine)

app.include_router(upload_router)