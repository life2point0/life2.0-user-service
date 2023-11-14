from pydantic import BaseModel
from .dto_config_base import ConfigBase

class TokenDTO(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    realm_access: dict
    resource_access: dict

    class Config(ConfigBase):
        pass