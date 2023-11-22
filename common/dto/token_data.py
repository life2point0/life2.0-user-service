from pydantic import BaseModel
from .dto_config_base import ConfigBase
from typing import List

class RealmAccess(BaseModel):
    roles: List[str]
class TokenDTO(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    realm_access: RealmAccess
    resource_access: dict

    class Config(ConfigBase):
        pass