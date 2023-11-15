from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, Table, Integer
from .base import TimeStampedModel
from sqlalchemy.dialects.postgresql import UUID


def get_user_association_table(associated_table: str, associate_key: str = 'associate_id', association_table_name: str = None):
    association_table = association_table_name if association_table_name else f'user_{associated_table}'
    return Table(
        association_table, 
        TimeStampedModel.metadata,
        Column('user_id', UUID, ForeignKey('users.id'), primary_key=True),
        Column(associate_key, UUID, ForeignKey(f'{associated_table}.id'), primary_key=True),
        Column('user_preferred_sort_order', Integer, nullable=True, default=None),
        PrimaryKeyConstraint('user_id', associate_key, name=f'pk__users__{associated_table}')
    )
