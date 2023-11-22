from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO, PlaceDTO, BaseDTO
from uuid import UUID
from typing import Optional, List
from common.dto import FileDTO

class CommunityMemberDTO(BaseDTO):
    id: UUID
    first_name: str
    last_name: str
    profile_photo: FileDTO

class CommunityDTO(IDNamePairResponseDTO):
    description: str
    image: Optional[FileDTO] = None
    tagged_places: Optional[List[PlaceDTO]] = None
    tagged_interests: Optional[List[IDNamePairResponseDTO]] = None
    tagged_skills: Optional[List[IDNamePairResponseDTO]] = None
    tagged_languages: Optional[List[IDNamePairResponseDTO]] = None
    tagged_occupations: Optional[List[IDNamePairResponseDTO]] = None
    members: Optional[List[CommunityMemberDTO]] = None
    created_at: int
    created_by: CommunityMemberDTO



class CommunityCreateRequestDTO(IDNamePairRequestDTO):
    description: str
    image: Optional[UUID] = None
    tagged_places: Optional[List[str]] = None
    tagged_interests: Optional[List[str]] = None
    tagged_skills: Optional[List[str]] = None
    tagged_languages: Optional[List[str]] = None
    tagged_occupations: Optional[List[str]] = None
    members: Optional[List[str]] = None