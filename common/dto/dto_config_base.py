from common.util import to_camel
from sqlalchemy import UUID

class ConfigBase:
    alias_generator = to_camel
    populate_by_name = True
    json_encoders = {
        UUID: lambda v: str(v)
    }