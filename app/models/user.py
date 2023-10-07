from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import TimeStampedModel
from uuid import uuid4
from .association_tables import user_occupations_table, user_past_locations_table, user_interests_table


class UserModel(TimeStampedModel):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_country_code = Column(String)
    phone_number = Column(String)
    email = Column(String, nullable=False, unique=True)
    description = Column(Text)

    place_of_origin_id = Column(UUID(as_uuid=True), ForeignKey('places.id'))
    current_location_id = Column(UUID(as_uuid=True), ForeignKey('places.id'))

    place_of_origin = relationship("PlaceModel", foreign_keys=[place_of_origin_id], back_populates="users_originally_from_here")
    current_location = relationship("PlaceModel", foreign_keys=[current_location_id], back_populates="users_currently_here")
    past_locations = relationship("PlaceModel", secondary=user_past_locations_table, back_populates="users_previously_here")
    occupations = relationship("OccupationModel", secondary=user_occupations_table, back_populates='users')
    interests = relationship("InterestModel", secondary=user_interests_table, back_populates='users')
