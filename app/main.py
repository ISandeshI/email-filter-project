from fastapi import FastAPI
from app.routes.upload import router as upload_router
from app.database.connection import engine
from app.database.models import Base
from app.routes.dashboard import router as dashboard_router
from app.routes.contacts import router as contacts_router
from app.routes.history import router as history_router
from fastapi.middleware.cors import CORSMiddleware
from app.routes.unsubscribed import router as unsubscribed_router
from app.routes import bounced

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
Base.metadata.create_all(bind=engine)

app.include_router(upload_router)
app.include_router(dashboard_router)
app.include_router(contacts_router)
app.include_router(history_router)
app.include_router(unsubscribed_router)
app.include_router(bounced.router)