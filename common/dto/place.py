from pydantic import BaseModel
from typing import Optional

class LatLongDTO(BaseModel):
    lat: float
    lng: float

class PlaceDTO(BaseModel):
    id: Optional[str] = None
    name: str
    geolocation: LatLongDTO