from fastapi import FastAPI, File, HTTPException, UploadFile
from app.services.csvprocessor import MissingPolicy, clean, statistics
import os
import tempfile
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg
import alembic

import enum


class Operation(enum.Enum):
    CLEAN = 'clean'
    STATISTICS = 'statistics' 

app = FastAPI()


@app.post('/jobs')
async def Job(
    file: UploadFile = File(...),
    required_columns: list[str] | None = None,
    missing_value_policy: MissingPolicy = MissingPolicy.PRESERVE,
    operation:Operation = Operation.CLEAN,
):
    if file.content_type != 'text/csv':
        raise HTTPException(
            status_code=400,
            detail="Incorrect file type. Please upload a CSV.",
        )

    if operation not in {'clean', 'statistics'}:
        raise HTTPException(
            status_code=400,
            detail="Choose either clean or statistics",
        )

    temporary_file = tempfile.NamedTemporaryFile(
        mode='wb',
        suffix='.csv',
        delete=False,
    )

    try:
        contents = await file.read()
        temporary_file.write(contents)
        temporary_file.close()

        if Operation.STATISTICS:
            return statistics(temporary_file.name)

        cleaned_data = clean(
            temporary_file.name,
            required_columns or [],
            missing_value_policy,
        )
        cleaned_data = cleaned_data.astype(object).where(
        pd.notna(cleaned_data), None
)
        return {
            'operation': 'clean',
            'data': cleaned_data.to_dict(orient='records'),
        }
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        if not temporary_file.file.closed:
            temporary_file.close()
        if os.path.exists(temporary_file.name):
            os.unlink(temporary_file.name)
