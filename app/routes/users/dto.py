from fastapi import FastAPI
from pydantic import Field
from typing import List, Optional
from common.util import to_camel
from pydantic import EmailStr
from common.dto import PlaceDTO, IDNamePairResponseDTO, BaseDTO
from uuid import UUID

app = FastAPI()

NAME_REGEX = "^[a-zA-Z .]+$"


class UserDTO(BaseDTO):
    first_name: str = Field(..., example="John", pattern=NAME_REGEX)
    last_name: str = Field(..., example="Smith", pattern=NAME_REGEX)
    phone_country_code: str = Field(None, example="123456789", pattern="^\d{1,3}$")
    phone_number: str = Field(None, example="1234567890", pattern="^\d{10}$")
    email: EmailStr
    place_of_origin: PlaceDTO
    past_locations: List[PlaceDTO]
    current_place: PlaceDTO
    description: str = Field(..., max_length=600)
    occupations: List[str]
    interests: List[str] = []


class PhotoDTO(BaseDTO):
    id: UUID
    url: Optional[str] = Field('')

class UserPartialDTO(BaseDTO):
    id: UUID = Field(None)
    first_name: Optional[str] = Field(None, example="John", pattern=NAME_REGEX)
    last_name: Optional[str] = Field(None, example="Smith", pattern=NAME_REGEX)
    phone_country_code: Optional[str] = Field(None, example="123456789", pattern="^\d{1,3}$")
    phone_number: Optional[str] = Field(None, example="1234567890", pattern="^\d{10}$")
    email: Optional[EmailStr] = None
    place_of_origin: Optional[PlaceDTO] = None  # Assuming PlaceDTO is imported or defined elsewhere
    past_locations: Optional[List[PlaceDTO]] = []
    current_place: Optional[PlaceDTO] = None
    description: Optional[str] = Field(None, max_length=600)
    occupations: Optional[List[IDNamePairResponseDTO]] = []
    interests: Optional[List[IDNamePairResponseDTO]] = []
    skills: Optional[List[IDNamePairResponseDTO]] = []
    languages: Optional[List[IDNamePairResponseDTO]] = []
    photos: Optional[List[PhotoDTO]]

class UserUpdateDTO(UserPartialDTO):
    id: Optional[UUID] = Field(None)
    current_place: Optional[str] = None
    place_of_origin: Optional[str] = None
    past_locations: Optional[List[str]] = None
    occupations: Optional[List[UUID]] = None
    interests: Optional[List[UUID]] = None
    skills: Optional[List[UUID]] = None
    languages: Optional[List[UUID]] = None
    photos: Optional[List[UUID]] = None

class UserSignupDTO(BaseDTO):
    first_name: str = Field(..., example="John", pattern=NAME_REGEX)
    last_name: str = Field(..., example="Smith", pattern=NAME_REGEX)
    email: EmailStr = None
    password: str

class JoinCommunityDTO(BaseDTO):
    community_id: str = Field(...)

