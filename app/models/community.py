from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import TimeStampedModel
from sqlalchemy.orm import relationship
from .id_name_pair import create_id_name_pair_model
from .association_tables import get_community_association_table

table_name = 'communities'
singular_name = 'community'

IDNamePairModel = create_id_name_pair_model(table_name)

community_members_table = get_community_association_table('users', 'user_id', association_table_name='community_members')
community_tagged_places_table = get_community_association_table('places', 'place_id', association_table_name='community_tagged_places')
community_tagged_interests_table = get_community_association_table('interests', 'interest_id', association_table_name='community_tagged_interests')
community_tagged_skills_table = get_community_association_table('skills', 'skill_id', association_table_name='community_tagged_skills')
community_tagged_languages_table = get_community_association_table('languages', 'language_id', association_table_name='community_tagged_languages')
community_tagged_occupations_table = get_community_association_table('occupations', 'occupation_id', association_table_name='community_tagged_occupations')

class CommunityModel(IDNamePairModel, TimeStampedModel):

    description = Column(String(500), nullable=False)
    image_id = Column(UUID, ForeignKey('files.id', name='fk__communities.image_id__files.id'))

    image = relationship("FileModel", foreign_keys=[image_id])
    members = relationship('PlaceModel', secondary=community_members_table, back_populates=table_name)
    tagged_places = relationship('PlaceModel', secondary=community_tagged_places_table, back_populates=table_name)
    tagged_interests = relationship('InterestModel', secondary=community_tagged_interests_table, back_populates=table_name)
    tagged_skills = relationship('SkillModel', secondary=community_tagged_skills_table, back_populates=table_name)
    tagged_languages = relationship('LanguageModel', secondary=community_tagged_languages_table, back_populates=table_name)
    tagged_occupations = relationship('OccupationModel', secondary=community_tagged_occupations_table, back_populates=table_name)
