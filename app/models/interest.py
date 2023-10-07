from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from .base import TimeStampedModel
from uuid import uuid4
from sqlalchemy.orm import relationship
from .association_tables import user_interests_table

class InterestModel(TimeStampedModel):
    __tablename__ = 'interests'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)
    users = relationship('UserModel', secondary=user_interests_table, back_populates='interests')
