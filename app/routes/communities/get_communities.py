import logging
from fastapi import APIRouter, HTTPException, Depends
from app.settings import AppSettings
from stream_chat import StreamChat
from .util import get_community_recommendations
from app.dependencies import jwt_guard
from typing import Optional
from common.dto import TokenDTO, PaginatedResponseDTO, PaginationParams
from app.database import get_db
from .dto import CommunityDTO

logging.basicConfig(level=logging.DEBUG) 

get_communities_route = APIRouter()

@get_communities_route.get("")
def community_list(
    pagination_params: PaginationParams = Depends(),
    db = Depends(get_db), token_data: Optional[TokenDTO] = Depends(jwt_guard)
):
    user_id = token_data.sub if token_data else None
    try:
        if user_id is not None:
            communities, total = get_community_recommendations(db, user_id)
            return PaginatedResponseDTO[CommunityDTO](data=communities, total=total, **dict(pagination_params))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
