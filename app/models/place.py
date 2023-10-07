from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .base import TimeStampedModel
from uuid import uuid4
from .association_tables import user_past_locations_table

class PlaceModel(TimeStampedModel):
    __tablename__ = 'places'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)
    geolocation = Column(Geometry(geometry_type='POINT'), nullable=False)
    users_originally_from_here = relationship("UserModel", foreign_keys="UserModel.place_of_origin_id")
    users_currently_here = relationship("UserModel", foreign_keys="UserModel.current_location_id")
    users_previously_here = relationship("UserModel", secondary=user_past_locations_table, back_populates='past_locations')
