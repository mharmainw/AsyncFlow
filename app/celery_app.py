from celery import Celery
from app.config import settings


celery_app = Celery(
    "asyncflow",
    broker=settings.celery_broker_url,
    include=["app.tasks"],
)
