from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import TimeStampedModel
from sqlalchemy.orm import relationship
from .id_name_pair import create_id_name_pair_model
from .association_tables import get_community_association_table
from .place import community_tagged_places_table
from .interest import community_tagged_interests_table
from .skill import community_tagged_skills_table
from .language import community_tagged_languages_table
from .occupation import community_tagged_occupations_table

table_name = 'communities'
singular_name = 'community'
back_populates_property = f'tagged_{table_name}'

IDNamePairModel = create_id_name_pair_model(table_name)

community_members_table = get_community_association_table('users', 'user_id', association_table_name='community_members')

class CommunityModel(IDNamePairModel, TimeStampedModel):

    description = Column(String(500), nullable=False)
    image_id = Column(UUID, ForeignKey('files.id', name='fk__communities.image_id__files.id'))

    image = relationship("FileModel", foreign_keys=[image_id])
    members = relationship('UserModel', secondary=community_members_table, back_populates=table_name)
    tagged_places = relationship('PlaceModel', secondary=community_tagged_places_table, back_populates=back_populates_property)
    tagged_interests = relationship('InterestModel', secondary=community_tagged_interests_table, back_populates=back_populates_property)
    tagged_skills = relationship('SkillModel', secondary=community_tagged_skills_table, back_populates=back_populates_property)
    tagged_languages = relationship('LanguageModel', secondary=community_tagged_languages_table, back_populates=back_populates_property)
    tagged_occupations = relationship('OccupationModel', secondary=community_tagged_occupations_table, back_populates=back_populates_property)
