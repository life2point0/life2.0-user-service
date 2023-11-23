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
    photo: Optional[FileDTO] = None
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
    photo: Optional[UUID] = None
    tagged_places: Optional[List[str]] = None
    tagged_interests: Optional[List[UUID]] = None
    tagged_skills: Optional[List[UUID]] = None
    tagged_languages: Optional[List[UUID]] = None
    tagged_occupations: Optional[List[UUID]] = None
    members: Optional[List[UUID]] = None

class CommunityPatchRequestDTO(CommunityCreateRequestDTO):
    members: Optional[None] = None
    description: Optional[str] = None