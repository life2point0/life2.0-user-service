from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from .base import TimeStampedModel
from uuid import uuid4
from sqlalchemy.orm import relationship
from .association_tables import user_occupations_table

class OccupationModel(TimeStampedModel):
    __tablename__ = 'occupations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)
    users = relationship('UserModel', secondary=user_occupations_table, back_populates='occupations')
