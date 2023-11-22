from stream_chat import StreamChat
from app.settings import AppSettings
import logging
from uuid import UUID
from typing import Dict

stream_client = StreamChat(api_key=AppSettings.STREAM_ACCESS_KEY_ID, api_secret=AppSettings.STREAM_SECRET_ACCESS_KEY)

# Function to create or update a Stream Chat channel
def upsert_stream_chat_channel(channel_id: UUID, user_id: UUID, channel_data: Dict, channel_type: str = 'community'):
    try:
        channel = stream_client.channel(channel_type, channel_id, channel_data)
        channel.create(user_id)
    except Exception as e:
        logging.error(f"Failed to upsert Stream Chat channel: {e}")
        raise e