from sqlalchemy import Column, String, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .base import TimeStampedModel
from uuid import uuid4
from .association_tables import get_user_association_table

user_past_locations_table = get_user_association_table('places', associate_key='place_id', association_table_name='user_past_locations')
class PlaceModel(TimeStampedModel):
    __tablename__ = 'places'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    google_place_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    geolocation = Column(Geometry(geometry_type='POINT'), nullable=False)
    additional_details = Column(JSON, nullable=True)
    users_originally_from_here = relationship("UserModel", foreign_keys="UserModel.place_of_origin_id")
    users_currently_here = relationship("UserModel", foreign_keys="UserModel.current_place_id")
    users_previously_here = relationship("UserModel", secondary=user_past_locations_table, back_populates='past_locations')

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        geolocation = kwargs.get('geolocation')
        self.geolocation = f"POINT({geolocation['lat']} {geolocation['lng']})"
        self.google_place_id = kwargs.get('google_place_id')
        self.additional_details = kwargs.get('additional_details')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk__places__id'),
        UniqueConstraint('id', name='uq__places__id'),
        UniqueConstraint('google_place_id', name='uq__places__google_place_id'),
    )
