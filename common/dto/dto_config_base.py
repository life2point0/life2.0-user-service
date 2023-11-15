from common.util import to_camel
from sqlalchemy import UUID

class ConfigBase:
    orm_mode = True
    alias_generator = to_camel
    populate_by_name = True
    from_attributes=True
    json_encoders = {
        UUID: lambda v: str(v)
    }