from sqlalchemy import Column, event, Enum, DateTime, UUID, PrimaryKeyConstraint, ForeignKeyConstraint
from datetime import datetime
from sqlalchemy.orm import relationship, Session
from sqlalchemy.orm.attributes import flag_modified
from uuid import uuid4
from .base import TimeStampedModel

class UserConnectionRequestModel(TimeStampedModel):
    __tablename__ = 'user_connection_requests'

    id = Column(UUID(as_uuid=True), default=uuid4, )
    status = Column(Enum('PENDING', 'ACCEPTED', 'REJECTED', name='user_connection_request_status'), default='pending', name='request_status')
    requester_user_id = Column(UUID(as_uuid=True), nullable=False)
    requested_user_id = Column(UUID(as_uuid=True), nullable=False)
    decided_at = Column(DateTime(timezone=True), nullable=True)

    requester_user = relationship("UserModel", foreign_keys=[requester_user_id], back_populates="outgoing_connection_requests")
    requested_user = relationship("UserModel", foreign_keys=[requested_user_id], back_populates="incoming_connection_requests")

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk__user_connection_requests__id'),
        ForeignKeyConstraint([requester_user_id], ['users.id'], name='fk__user_connection_requests.requester_user_id__users.id'),
        ForeignKeyConstraint([requested_user_id], ['users.id'], name='fk__user_connection_requests.requested_user_id__users.id')
    )

# Event listener to update decided_at when status is changed
def update_decided_at(mapper, connection, target):
    if isinstance(target._sa_instance_state.session, Session):
        if target._sa_instance_state.attrs.get('status', False):
            previous_status = target._sa_instance_state.attrs.status.history.deleted[0] if target._sa_instance_state.attrs.status.history.deleted else None
            new_status = target._sa_instance_state.attrs.status.history.added[0] if target._sa_instance_state.attrs.status.history.added else None
            
            if previous_status == 'pending' and (new_status == 'accepted' or new_status == 'rejected'):
                target.decided_at = datetime.now()
                flag_modified(target, "decided_at")

event.listen(UserConnectionRequestModel, 'before_update', update_decided_at)
