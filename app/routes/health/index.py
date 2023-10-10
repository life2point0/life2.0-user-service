import logging
from fastapi import APIRouter, HTTPException, Request
import requests
from app.constants import COMETCHAT_BASE_URL, COMETCHAT_KEY

logging.basicConfig(level=logging.DEBUG) 
router = APIRouter()

@router.get("")
def community_list(request: Request):
    return { "status": "alive" }