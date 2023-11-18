from pydantic import BaseModel, validator
from .dto_config_base import ConfigBase
from datetime import datetime
from typing import Any
import time

class BaseDTO(BaseModel):
    class Config(ConfigBase):
        pass

    @classmethod
    def trim_string(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value
    
    @classmethod
    def datetime_to_epoch_millis(cls, value: Any):
        if isinstance(value, datetime):
            return int(time.mktime(value.timetuple()) * 1000 + value.microsecond / 1000)
        return value

    _preprocess_all_fields = validator("*", pre=True, allow_reuse=True)(trim_string)
    _convert_datetime_to_millis = validator("*", pre=True, allow_reuse=True)(datetime_to_epoch_millis)
