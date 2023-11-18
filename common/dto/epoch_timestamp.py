from pydantic import BaseModel, validator, conint
from datetime import datetime
import time

EpochMillis = conint(ge=0)

class PastEpochTimestamp(BaseModel):
    timestamp: EpochMillis

    @validator('timestamp', pre=True)
    def convert_datetime_to_epoch_millis(cls, v):
        if isinstance(v, datetime):
            # Convert datetime to Unix timestamp in milliseconds
            return int(time.mktime(v.timetuple()) * 1000 + v.microsecond / 1000)
        return v

    # TODO: Only for responses. Not for Requests. Separate this out
    @validator('timestamp', pre=False)
    def ensure_past_timestamp(cls, v):
        # Ensure the timestamp does not represent a future time
        current_time_ms = int(time.time() * 1000)
        if v <= current_time_ms:
            return v
        else:
            raise ValueError("Timestamp cannot be in the future")
