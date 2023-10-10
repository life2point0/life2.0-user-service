import logging
from fastapi import APIRouter, HTTPException, Request
import requests
from app.constants import COMETCHAT_BASE_URL, COMETCHAT_KEY

logging.basicConfig(level=logging.DEBUG) 
router = APIRouter()

@router.get("")
def community_list(request: Request):
    try:
        res = requests.get(
            f"{COMETCHAT_BASE_URL}/groups",
            headers={
                "ApiKey": COMETCHAT_KEY
            },
            params=request.query_params,
        )
        return res.json()
    except HTTPException as e:
        logging.error(e)
        raise e