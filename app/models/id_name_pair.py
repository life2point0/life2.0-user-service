from sqlalchemy import Column, PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID, CITEXT
from sqlalchemy.orm import relationship, declared_attr
from uuid import uuid4
from .base import BaseModel

def create_id_name_pair_model(table_name: str):
    class IDNamePairModel(BaseModel):
        __tablename__ = table_name
        __abstract__ = True
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
        name = Column(CITEXT(), nullable=False)  
        created_by_user_id = Column(UUID, nullable=False)

        @declared_attr
        def created_by(cls):
            return relationship("UserModel", foreign_keys=[cls.created_by_user_id])  

        __table_args__ = (
            PrimaryKeyConstraint('id', name=f'pk__{table_name}__id'),
            UniqueConstraint('id', name=f'uq__{table_name}__id'),
            UniqueConstraint('name', name=f'uq__{table_name}__name'),
            ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=f'fk__{table_name}.created_by__users.id')
        )
    return IDNamePairModel
