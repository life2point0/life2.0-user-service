from sqlalchemy import Column, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON, BOOLEAN
from .base import TimeStampedModel
from uuid import uuid4

class NotificationModel(TimeStampedModel):
    __tablename__ = 'notifications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    data = Column(JSON, nullable=False)
    target_user_id = Column(UUID, nullable=False)
    is_read = Column(BOOLEAN, nullable=False, default=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk__notifications__id'),
        ForeignKeyConstraint(['target_user_id'], ['users.id'], name=f'fk__notifications.target_user_id__users.id'),
    )
