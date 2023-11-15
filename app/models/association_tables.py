from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, Table, Integer
from .base import TimeStampedModel
from sqlalchemy.dialects.postgresql import UUID


def get_user_association_table(associate_table: str, associate_key: str = 'associate_id'):
    return Table(
        f'user_{associate_table}', 
        TimeStampedModel.metadata,
        Column('user_id', UUID, ForeignKey('users.id'), primary_key=True),
        Column(associate_key, UUID, ForeignKey(f'{associate_table}.id'), primary_key=True),
        Column('user_preferred_sort_order', Integer, nullable=True, default=None),
        PrimaryKeyConstraint('user_id', associate_key, name=f'pk_users_{associate_table}')
    )

user_past_locations_table = Table('user_past_locations', TimeStampedModel.metadata,
    Column('user_id', UUID, ForeignKey('users.id'), primary_key=True),
    Column('place_id', UUID, ForeignKey('places.id'), primary_key=True),
)
