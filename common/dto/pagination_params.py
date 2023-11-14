from typing import Optional
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    per_page: Optional[int] = Field(10, alias="perPage")
    page_number: Optional[int] = Field(0, alias="pageNumber")
    query: Optional[str] = ''
