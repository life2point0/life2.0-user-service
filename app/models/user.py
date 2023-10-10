from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import TimeStampedModel
from uuid import uuid4
from .association_tables import user_occupations_table, user_past_locations_table, user_interests_table
from .place import PlaceModel


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

    def __init__(self, **kwargs):
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.phone_country_code = kwargs.get('phone_country_code')
        self.phone_number = kwargs.get('phone_number')
        self.email = kwargs.get('email')
        self.description = kwargs.get('description')

        place_of_origin = PlaceModel(**kwargs.get('place_of_origin'))
        current_location = PlaceModel(**kwargs.get('current_location'))
        past_locations = kwargs.get('past_locations', [])
        occupations = kwargs.get('occupations', [])
        interests = kwargs.get('interests', [])

        if place_of_origin:
            self.place_of_origin = place_of_origin
        if current_location:
            self.current_location = current_location
        if past_locations:
            self.past_locations = past_locations
        if occupations:
            self.occupations = occupations
        if interests:
            self.interests = interests
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
