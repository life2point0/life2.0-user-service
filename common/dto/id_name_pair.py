from pydantic import BaseModel

class IDNamePairDTO(BaseModel):
    id: str
    name: str