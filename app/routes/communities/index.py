import logging
from fastapi import APIRouter, HTTPException, Request
from app.settings import AppSettings
from stream_chat import StreamChat


logging.basicConfig(level=logging.DEBUG) 
router = APIRouter()

@router.get("")
def community_list():
    try:
        client = StreamChat(api_key=AppSettings.STREAM_ACCESS_KEY_ID, api_secret=AppSettings.STREAM_SECRET_ACCESS_KEY)
        filter_conditions = {"type": "community"}
        sort = {"created_at": -1}
        response = client.query_channels(filter_conditions, sort=sort)
        return response["channels"]
    except HTTPException as e:
        logging.error(e)
        raise e
