from datetime import datetime

def datetime_from_epoch_ms(epoch_ms: int) -> datetime:
    # Convert milliseconds to seconds and microseconds
    seconds = epoch_ms // 1000
    microseconds = (epoch_ms % 1000) * 1000

    # Create a datetime object from seconds and add microseconds
    return datetime.utcfromtimestamp(seconds).replace(microsecond=microseconds)