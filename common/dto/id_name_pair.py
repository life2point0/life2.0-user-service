from .base import BaseDTO
from pydantic import UUID4

class IDNamePairResponseDTO(BaseDTO):
    id: UUID4
    name: str


class IDNamePairRequestDTO(BaseDTO):
    name: str