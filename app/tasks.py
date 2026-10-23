from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Job, Operation, Status
from app.services.csvprocessor import MissingPolicy, clean, statistics


@celery_app.task(name="app.tasks.process_job")
def process_job(job_id: str):
    db = SessionLocal()
    job = None

    try:
        job = db.get(Job, UUID(job_id))

        if job is None:
            raise ValueError(f"Job {job_id} was not found")

        job.status = Status.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        job.completed_at = None
        job.error_message = None
        job.attempt_count += 1
        db.commit()

        if job.operation == Operation.CLEAN:
            cleaned_data = clean(
                job.input_path,
                job.required_columns or [],
                job.missing_policy or MissingPolicy.PRESERVE,
            )

            output_path = Path(job.input_path).parent / "output.csv"
            cleaned_data.to_csv(output_path, index=False)
            job.output_path = str(output_path)

        elif job.operation == Operation.STATISTICS:
            job.result = statistics(job.input_path)

        else:
            raise ValueError(f"Unsupported operation: {job.operation}")

        job.status = Status.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

        return str(job.id)

    except Exception as error:
        db.rollback()

        if job is not None:
            job.status = Status.FAILED
            job.completed_at = datetime.now(timezone.utc)
            job.error_message = str(error)
            db.commit()

        raise

    finally:
        db.close()