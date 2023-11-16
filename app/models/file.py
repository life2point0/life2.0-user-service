from sqlalchemy import Column, String, UniqueConstraint, PrimaryKeyConstraint
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

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk__files__id'),
    )

    @hybrid_property
    def url(self):
        return f"https://{self.cdn_host}/{self.folder}/{self.id}.{self.file_extension}"
