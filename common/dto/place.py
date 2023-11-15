from typing import Optional
from .base import BaseDTO
from uuid import UUID
from pydantic import validator
from geoalchemy2.shape import to_shape, WKBElement
from uuid import UUID

class LatLongDTO(BaseDTO):
    lat: float
    lng: float

class PlaceDTO(BaseDTO):
    id: Optional[UUID] = None
    name: str
    google_place_id: str
    geolocation: LatLongDTO
    
    @validator('geolocation', pre=True, allow_reuse=True)
    def convert_wkb_to_geolocation(cls, v, values, **kwargs):
        # Assuming 'v' is a WKBElement instance from GeoAlchemy
        if isinstance(v, WKBElement):
            # Convert WKBElement to a Shapely geometry
            geom = to_shape(v)
            return LatLongDTO(lat=geom.y, lng=geom.x)
        return v