from sqlalchemy import Column, ForeignKey, Integer, Table
from .base import date_columns, TimeStampedModel
from sqlalchemy.dialects.postgresql import UUID


user_occupations_table = Table('user_occupations', TimeStampedModel.metadata,
    Column('user_id', UUID, ForeignKey('users.id'), primary_key=True),
    Column('occupation_id', UUID, ForeignKey('occupations.id'), primary_key=True),
)

user_past_locations_table = Table('user_past_locations', TimeStampedModel.metadata,
    Column('user_id', UUID, ForeignKey('users.id'), primary_key=True),
    Column('place_id', UUID, ForeignKey('places.id'), primary_key=True),
)

user_interests_table = Table('user_interests', TimeStampedModel.metadata,
    Column('user_id', UUID, ForeignKey('users.id'), primary_key=True),
    Column('interest_id', UUID, ForeignKey('interests.id'), primary_key=True),
)