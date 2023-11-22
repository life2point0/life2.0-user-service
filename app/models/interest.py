from .id_name_pair import create_id_name_pair_model
from .base import TimeStampedModel
from .association_tables import get_user_association_table, get_community_association_table
from sqlalchemy.orm import relationship

table_name = 'interests'
singular_name = 'interest'

IDNamePairModel = create_id_name_pair_model(table_name)

user_interests_table = get_user_association_table(table_name, f'{singular_name}_id')
community_tagged_interests_table = get_community_association_table('interests', 'interest_id', association_table_name='community_tagged_interests')


class InterestModel(IDNamePairModel, TimeStampedModel):
    users = relationship('UserModel', secondary=user_interests_table, back_populates=table_name)
    tagged_communities = relationship("CommunityModel", secondary=community_tagged_interests_table, back_populates='tagged_interests')
