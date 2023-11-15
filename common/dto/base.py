from pydantic import BaseModel, validator
from .dto_config_base import ConfigBase

class BaseDTO(BaseModel):
    class Config(ConfigBase):
        pass

    @classmethod
    def trim_string(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    _preprocess_all_fields = validator("*", pre=True, allow_reuse=True)(trim_string)
