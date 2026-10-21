from .database import Base
from sqlalchemy import Column,Integer,String,Boolean , ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from enum import Enum
from .services.csvprocessor import MissingPolicy
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import JSON
from sqlalchemy import Enum as SQLAlchemyEnum


class Status(Enum):
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

class Operation(Enum):
    CLEAN = 'clean'
    STATISTICS = 'statistics' 



class Job(Base):
    __tablename__ = 'jobs'


    id = Column(UUID(as_uuid=True),primary_key = True,nullable = False,default=uuid.uuid4)
    original_filename = Column(String,nullable = False)
    operation = Column(SQLAlchemyEnum(Operation),nullable = False)
    status = Column(SQLAlchemyEnum(Status),nullable = False)
    missing_policy = Column(SQLAlchemyEnum(MissingPolicy))
    required_columns = Column(JSON,nullable = False)
    created_at = Column(TIMESTAMP(timezone=True),nullable = False,server_default=text('now()'))
    started_at = Column(TIMESTAMP(timezone=True),nullable = False,server_default=text('now()'))
    error_message = Column(String,nullable = True)
    output_path = Column(String,nullable= True)
    result = Column(JSON,nullable = True)


