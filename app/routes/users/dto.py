from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from common.util import to_camel
from pydantic import EmailStr
from common.dto import PlaceDTO
from sqlalchemy import UUID

app = FastAPI()

NAME_REGEX = "^[a-zA-Z .]+$"

class UserDTO(BaseModel):
    first_name: str = Field(..., example="John", pattern=NAME_REGEX)
    last_name: str = Field(..., example="Smith", pattern=NAME_REGEX)
    phone_country_code: str = Field(None, example="123456789", pattern="^\d{1,3}$")
    phone_number: str = Field(None, example="1234567890", pattern="^\d{10}$")
    email: EmailStr
    place_of_origin: PlaceDTO
    past_locations: List[PlaceDTO]
    current_location: PlaceDTO
    description: str = Field(..., max_length=600)
    occupations: List[str]
    interests: List[str] = []

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class UserPartialDTO(BaseModel):
    id: Optional[str] = Field(None)
    first_name: Optional[str] = Field(None, example="John", pattern=NAME_REGEX)
    last_name: Optional[str] = Field(None, example="Smith", pattern=NAME_REGEX)
    phone_country_code: Optional[str] = Field(None, example="123456789", pattern="^\d{1,3}$")
    phone_number: Optional[str] = Field(None, example="1234567890", pattern="^\d{10}$")
    email: Optional[EmailStr] = None
    place_of_origin: Optional[PlaceDTO] = None  # Assuming PlaceDTO is imported or defined elsewhere
    past_locations: Optional[List[PlaceDTO]] = []
    current_location: Optional[PlaceDTO] = None
    description: Optional[str] = Field(None, max_length=600)
    occupations: Optional[List[any]] = []
    interests: Optional[List[any]] = []

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        json_encoders = {
            UUID: lambda v: str(v)
        }

class UserSignupDTO(BaseModel):
    first_name: str = Field(..., example="John", pattern=NAME_REGEX)
    last_name: str = Field(..., example="Smith", pattern=NAME_REGEX)
    email: EmailStr = None
    password: str

    class Config:
        alias_generator = to_camel
        populate_by_name = True

class JoinCommunityDTO(BaseModel):
    community_id: str = Field(...)
    class Config:
        alias_generator = to_camel
        populate_by_name = True
        json_encoders = {
            UUID: lambda v: str(v)
        }


class TokenDTO(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    realm_access: dict
    resource_access: dict