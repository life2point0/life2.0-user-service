from .base import BaseDTO
from typing import Generic, List, TypeVar

DataType = TypeVar('DataType')

class PaginatedResponseDTO(BaseDTO, Generic[DataType]):
    data: List[DataType]
    page_number: int
    per_page: int
    total: int
