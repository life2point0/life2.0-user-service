from sqlalchemy import Column, String, ForeignKey, Text, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from .base import TimeStampedModel
from uuid import uuid4
from .place import PlaceModel, user_past_places_table
from .occupation import user_occupations_table
from .skill import user_skills_table
from .interest import user_interests_table
from .language import user_languages_table
from .association_tables import get_user_association_table
from .community import community_members_table

user_photos_table = get_user_association_table(
    'files', 
    associate_key='photo_id', 
    association_table_name='user_photos'
)


class UserModel(TimeStampedModel):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_country_code = Column(String)
    phone_number = Column(String)
    email = Column(String, nullable=False)
    description = Column(Text)

    place_of_origin_id = Column(UUID(as_uuid=True), ForeignKey('places.id', name='fk__users__place_of_origin_id__places.id'))
    current_place_id = Column(UUID(as_uuid=True), ForeignKey('places.id', name='fk__users__current_place_id__places.id'))

    place_of_origin = relationship("PlaceModel", foreign_keys=[place_of_origin_id], back_populates="users_originally_from_here")
    current_place = relationship("PlaceModel", foreign_keys=[current_place_id], back_populates="users_currently_here")
    past_places = relationship("PlaceModel", secondary=user_past_places_table, back_populates="users_previously_here")
    occupations = relationship("OccupationModel", secondary=user_occupations_table, back_populates='users')
    interests = relationship("InterestModel", secondary=user_interests_table, back_populates='users')
    skills = relationship("SkillModel", secondary=user_skills_table, back_populates='users')
    languages = relationship("LanguageModel", secondary=user_languages_table, back_populates='users')
    photos = relationship("FileModel", secondary=user_photos_table)
    communities = relationship("CommunityModel", secondary=community_members_table, back_populates="members")
    connected_users = relationship(
        "UserModel",
        secondary="user_connections",
        primaryjoin="UserModel.id==UserConnectionModel.user_id",
        secondaryjoin="UserModel.id==UserConnectionModel.connected_user_id",
        viewonly=True
    )
    incoming_connection_requests = relationship(
        "UserConnectionRequestModel",
        foreign_keys="[UserConnectionRequestModel.requested_user_id]",
        back_populates="requested_user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    outgoing_connection_requests = relationship(
        "UserConnectionRequestModel",
        foreign_keys="[UserConnectionRequestModel.requester_user_id]",
        back_populates="requester_user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @hybrid_property
    def joined_at(self):
        return self.created_at
    

    @hybrid_property
    def profile_photo(self):
        return self.photos[0] if len(self.photos) > 0 else None
    
    __table_args__ = (
        PrimaryKeyConstraint('id', name=f'pk__users__id'),
        UniqueConstraint('id', name=f'uq__users__id'),
        UniqueConstraint('email', name=f'uq__users__email'),
    )

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.phone_country_code = kwargs.get('phone_country_code')
        self.phone_number = kwargs.get('phone_number')
        self.email = kwargs.get('email')
        self.description = kwargs.get('description')
        self.created_at = kwargs.get('created_at')

        place_of_origin = PlaceModel(**kwargs.get('place_of_origin')) if kwargs.get('place_of_origin') is not None else None
        current_place = PlaceModel(**kwargs.get('current_place')) if kwargs.get('current_place') is not None else None
        past_places = kwargs.get('past_places', [])
        occupations = kwargs.get('occupations', [])
        interests = kwargs.get('interests', [])

        if place_of_origin:
            self.place_of_origin = place_of_origin
        if current_place:
            self.current_place = current_place
        if past_places:
            self.past_places = past_places
        if occupations:
            self.occupations = occupations
        if interests:
            self.interests = interests
    
    def as_dict(self):
        user_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        user_dict['id'] = str(user_dict['id'])
        return user_dict
