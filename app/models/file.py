from sqlalchemy import Column, String, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2 import Geometry
from .base import TimeStampedModel
from uuid import uuid4

class FileModel(TimeStampedModel):
    __tablename__ = 'files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    folder = Column(String, default='', nullable=True)
    file_extension = Column(String, default='', nullable=True)
    file_name = Column(String, default='', nullable=True)
    bucket = Column(String, nullable=False)
    cdn_host = Column(String, nullable=False)
    created_by_user_id = Column(UUID, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk__files__id'),
        UniqueConstraint('id', name='uq__files__id'),
        ForeignKeyConstraint(['created_by_user_id'], ['users.id'], name=f'fk__files.created_by__users.id')
    )

    @hybrid_property
    def url(self):
        return f"https://{self.cdn_host}/{self.folder}/{self.id}.{self.file_extension}"
