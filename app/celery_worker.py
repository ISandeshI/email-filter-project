from celery import Celery

celery = Celery(
    "email_filter_project",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.services.filter_service"]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)