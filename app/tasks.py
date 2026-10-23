from datetime import datetime, timezone
from uuid import UUID

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Job, Status


@celery_app.task(name="app.tasks.process_job")
def process_job(job_id: str):
    db = SessionLocal()

    try:
        job = db.get(Job, UUID(job_id))

        if job is None:
            raise ValueError(f"Job {job_id} was not found")

        job.status = Status.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        job.attempt_count += 1

        db.commit()

        return str(job.id)
    finally:
        db.close()