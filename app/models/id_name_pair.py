from sqlalchemy import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from uuid import uuid4
from .base import BaseModel

def create_id_name_pair_model(table_name: str):
    class IDNamePairModel(BaseModel):
        __tablename__ = table_name
        __abstract__ = True
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
        name = Column(CITEXT(), nullable=False)    

        __table_args__ = (
            PrimaryKeyConstraint('id', name=f'pk_{table_name}_id'),
            UniqueConstraint('id', name=f'uq_{table_name}_id'),
            UniqueConstraint('name', name=f'uq_{table_name}_name'),
        )
    return IDNamePairModel