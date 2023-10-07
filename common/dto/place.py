from pydantic import BaseModel

class LatLongDTO(BaseModel):
    lat: float
    lng: float

class PlaceDTO(BaseModel):
    name: str
    geolocation: LatLongDTO