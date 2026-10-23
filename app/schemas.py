from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import Operation, Status


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: Status
    operation: Operation
    created_at: datetime
