import logging
from fastapi import APIRouter, HTTPException, Depends
from app.settings import AppSettings
from stream_chat import StreamChat
from .util import get_community_recommendations, get_community_search_results
from app.dependencies import jwt_optional
from typing import Optional
from common.dto import TokenDTO, PaginatedResponseDTO, PaginationParams
from app.database import get_db
from .dto import CommunityDTO

logging.basicConfig(level=logging.DEBUG) 

get_communities_route = APIRouter()

@get_communities_route.get("")
def community_list(
    pagination_params: PaginationParams = Depends(),
    ids: Optional[str] = None,
    db = Depends(get_db), 
    token_data: Optional[TokenDTO] = Depends(jwt_optional)
):
    user_id = token_data.sub if token_data else None
    page_number = pagination_params.page_number
    per_page = pagination_params.per_page
    query = pagination_params.query
    try:
        if user_id is not None and not query and not ids:
            communities, total = get_community_recommendations(
                db, 
                user_id, 
                per_page=per_page,
                page_number=page_number
            )
        else:
            communities, total = get_community_search_results(
                db, 
                per_page=per_page,
                page_number=page_number,
                query=query,
                ids=ids
            )
        return PaginatedResponseDTO[CommunityDTO](data=communities, total=total, **dict(pagination_params))
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
