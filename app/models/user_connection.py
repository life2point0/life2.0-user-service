from sqlalchemy import Column, PrimaryKeyConstraint, ForeignKeyConstraint, UniqueConstraint, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import TimeStampedModel  # Or your appropriate base class import
from uuid import uuid4

class UserConnectionModel(TimeStampedModel):
    __tablename__ = 'user_connections'

    id = Column(UUID(as_uuid=True), default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    connected_user_id = Column(UUID(as_uuid=True), nullable=False)
    connection_request_id = Column(UUID(as_uuid=True), nullable=False)

    connection_request = relationship('UserConnectionRequestModel', foreign_keys=[connection_request_id])

    # Ensure that user_id is always alphabetically before connected_user_id
    def __init__(self, user_id, connected_user_id, connection_request):
        self.user_id, self.connected_user_id = sorted([user_id, connected_user_id], key=lambda x: str(x))
        self.connection_request = connection_request

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk__user_connections__id'),
        UniqueConstraint('user_id', 'connected_user_id', name='uq__user_connections__user_id__connected_user_id'),
        ForeignKeyConstraint([user_id], ['users.id'], name='fk__user_connections.user_id__users.id'),
        ForeignKeyConstraint([connected_user_id], ['users.id'], name='fk__user_connections.connected_user_id__users.id'),
        ForeignKeyConstraint([connection_request_id], ['user_connection_requests.id'], name='fk__user_connections.conn_req_id__user_connection_requests.id'), # Not following convention in naming fk because of length constraints
    )

# Event listener to sort user IDs before insert
def sort_user_ids(mapper, connect, target):
    target.user_id, target.connected_user_id = sorted([target.user_id, target.connected_user_id], key=lambda x: str(x))

event.listen(UserConnectionModel, 'before_insert', sort_user_ids)
