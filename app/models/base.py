from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app.database import BaseModel

date_columns = [
    Column('created_at', DateTime(timezone=True), default=func.now()),
    Column('updated_at', DateTime(timezone=True), default=func.now(), onupdate=func.now()),
    Column('deleted_at', DateTime(timezone=True))
]

class TimeStampedModel(BaseModel):
    __abstract__ = True
    created_at, updated_at, deleted_at = date_columns
