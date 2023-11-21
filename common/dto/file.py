from typing import Optional
from pydantic import Field
from uuid import UUID
from .base import BaseDTO

class FileDTO(BaseDTO):
    id: UUID
    url: Optional[str] = Field('')