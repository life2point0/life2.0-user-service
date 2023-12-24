from stream_chat import StreamChat
from app.settings import AppSettings
import logging
from uuid import UUID
from typing import Dict

stream_client = StreamChat(api_key=AppSettings.STREAM_ACCESS_KEY_ID, api_secret=AppSettings.STREAM_SECRET_ACCESS_KEY)

# Function to create a Stream Chat channel
def create_stream_chat_channel(channel_id: UUID, user_id: UUID, channel_data: Dict, channel_type: str = 'community'):
    try:
        channel = stream_client.channel(channel_type, channel_id, channel_data)
        channel.create(user_id)

        # Rollback function for upsert
        def rollback():
            try:
                channel.delete()
            except Exception as e:
                logging.error(f"Failed to rollback Stream Chat channel creation: {e}")
                raise e
        
        return rollback

    except Exception as e:
        logging.error(f"Failed to create Stream Chat channel: {e}")
        raise e

# Function to update a Stream Chat channel
def update_stream_chat_channel(channel_id: UUID, channel_data: Dict, channel_type: str = 'community'):
    try:
        channel = stream_client.channel(channel_type, channel_id)
        # Fetch current channel state before updating
        current_state = channel.query()  # Adjust this method based on how to fetch channel data

        channel.update(channel_data)

        # Rollback function for update
        def rollback():
            try:
                rollback_data = {}
                for key, _ in channel_data.items():
                    rollback_data[key] = current_state['channel'][key]
                channel.update(rollback_data)
            except Exception as e:
                logging.error(f"Failed to rollback Stream Chat channel update: {e}")
                raise e

        return rollback

    except Exception as e:
        logging.error(f"Failed to update Stream Chat channel: {e}")
        raise e
    

# Function to create a Stream Chat channel
def create_one_to_one_stream_chat_channel(user_1: UUID, user_2: UUID, channel_type: str = 'messaging'):
    try:
        channel = stream_client.channel(channel_type, data={
            "members": [str(user_1), str(user_2)]
        })
        channel.create(str(user_1))
        return channel

    except Exception as e:
        logging.error(f"Failed to create Stream Chat channel: {e}")
        raise e


