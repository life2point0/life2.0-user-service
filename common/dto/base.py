from pydantic import BaseModel, validator
from common.util import to_camel

class BaseDTO(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
        from_attributes = True

    @classmethod
    def trim_string(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    _preprocess_all_fields = validator("*", pre=True, allow_reuse=True)(trim_string)
