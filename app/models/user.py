from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import TimeStampedModel
from uuid import uuid4
from .place import PlaceModel, user_past_locations_table
from .occupation import user_occupations_table
from .skill import user_skills_table
from .interest import user_interests_table
from .language import user_languages_table
from .association_tables import get_user_association_table

user_photos_table = get_user_association_table(
    'files', 
    associate_key='photo_id', 
    association_table_name='user_photos'
)


class UserModel(TimeStampedModel):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_country_code = Column(String)
    phone_number = Column(String)
    email = Column(String, nullable=False, unique=True)
    description = Column(Text)

    place_of_origin_id = Column(UUID(as_uuid=True), ForeignKey('places.id', name='fk__users__place_of_origin_id'))
    current_place_id = Column(UUID(as_uuid=True), ForeignKey('places.id', name='fk__users__current_place_id'))

    place_of_origin = relationship("PlaceModel", foreign_keys=[place_of_origin_id], back_populates="users_originally_from_here")
    current_place = relationship("PlaceModel", foreign_keys=[current_place_id], back_populates="users_currently_here")
    past_locations = relationship("PlaceModel", secondary=user_past_locations_table, back_populates="users_previously_here")
    occupations = relationship("OccupationModel", secondary=user_occupations_table, back_populates='users')
    interests = relationship("InterestModel", secondary=user_interests_table, back_populates='users')
    skills = relationship("SkillModel", secondary=user_skills_table, back_populates='users')
    languages = relationship("LanguageModel", secondary=user_languages_table, back_populates='users')
    photos = relationship("FileModel", secondary=user_photos_table)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.phone_country_code = kwargs.get('phone_country_code')
        self.phone_number = kwargs.get('phone_number')
        self.email = kwargs.get('email')
        self.description = kwargs.get('description')

        place_of_origin = PlaceModel(**kwargs.get('place_of_origin')) if kwargs.get('place_of_origin') is not None else None
        current_place = PlaceModel(**kwargs.get('current_place')) if kwargs.get('current_place') is not None else None
        past_locations = kwargs.get('past_locations', [])
        occupations = kwargs.get('occupations', [])
        interests = kwargs.get('interests', [])

        if place_of_origin:
            self.place_of_origin = place_of_origin
        if current_place:
            self.current_place = current_place
        if past_locations:
            self.past_locations = past_locations
        if occupations:
            self.occupations = occupations
        if interests:
            self.interests = interests
    
    def as_dict(self):
        user_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        user_dict['id'] = str(user_dict['id'])
        return user_dict
