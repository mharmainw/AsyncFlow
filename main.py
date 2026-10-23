import shutil
import uuid

from datetime import datetime, timezone
from pathlib import Path
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import Job, Operation, Status
from app.schemas import JobOut, JobStatusOut
from app.services.csvprocessor import MissingPolicy
from app.tasks import process_job
from fastapi.responses import FileResponse

app = FastAPI()


@app.post(
    "/jobs",
    response_model=JobOut,
    status_code=202,
)
async def create_job(
    file: UploadFile = File(...),
    required_columns: list[str] | None = None,
    missing_value_policy: MissingPolicy = MissingPolicy.PRESERVE,
    operation: Operation = Operation.CLEAN,
    db: Session = Depends(get_db),
):
    if file.content_type != 'text/csv':
        raise HTTPException(
            status_code=400,
            detail="Incorrect file type. Please upload a CSV.",
        )

    job_uuid = uuid.uuid4()
    job_directory = Path(settings.storage_path) / str(job_uuid)
    input_path = job_directory / "input.csv"

    try:
        job_directory.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail="Could not create job storage",
        ) from error

    try:
        with input_path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                destination.write(chunk)
    except OSError as error:
        shutil.rmtree(job_directory, ignore_errors=True)

        raise HTTPException(
            status_code=500,
            detail="Could not save uploaded file",
        ) from error

    job = Job(
        id=job_uuid,
        input_path=str(input_path),
        original_filename=file.filename or "input.csv",
        operation=operation,
        status=Status.QUEUED,
        missing_policy=missing_value_policy,
        required_columns=required_columns or [],
    )

    try:
        db.add(job)
        db.commit()
        db.refresh(job)
    except SQLAlchemyError as error:
        db.rollback()
        shutil.rmtree(job_directory, ignore_errors=True)

        raise HTTPException(
            status_code=500,
            detail="Could not create job",
        ) from error

    try:
        process_job.delay(str(job.id))
    except Exception as error:
        job.status = Status.FAILED
        job.completed_at = datetime.now(timezone.utc)
        job.error_message = f"Could not enqueue job: {error}"
        db.commit()

        raise HTTPException(
            status_code=503,
            detail="The job could not be queued",
        ) from error

    return job



@app.get('/jobs/{job_id}',response_model=JobStatusOut)
def jobstatus(job_id: uuid.UUID, db: Session = Depends(get_db)):

    job = db.get(Job,job_id)
    if job is None:
        raise HTTPException(status_code=404,detail="JOB NOT FOUND") 
    return job


@app.get('/jobs/{job_id}/result')
def result(job_id: uuid.UUID,db: Session = Depends(get_db)):
    job = db.get(Job,job_id)
    if job is None:
        raise HTTPException(status_code=404,detail="JOB NOT FOUND") 
    elif job.status != Status.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Job result is not available while status is {job.status.value}",
        )


    if job.operation == Operation.STATISTICS:
        return job.result
    else:
        if job.output_path:
            output_path = Path(job.output_path)
            if not output_path.is_file():
                raise HTTPException(status_code=404, detail="Job result was not found")
        else:
            raise HTTPException(status_code=404, detail="Job result was not found")
    

    return FileResponse(
        path = output_path,
        media_type= "text/csv",
        filename = f"processed_{job.original_filename}"
    )