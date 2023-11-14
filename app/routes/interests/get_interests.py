from fastapi import APIRouter, Depends
from common.dto import IDNamePairResponseDTO, PaginationParams, PaginatedResponseDTO, TokenDTO
from common.util import get_id_name_pair_paginated_response
from typing import Optional
from app.models.interest import InterestModel
from app.database import DatabaseSession, get_db;
import logging
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

get_interests_route = APIRouter()

@get_interests_route.get('', description='Interest List')
def get_interests(
    pagination_params: PaginationParams = Depends(),
    ids: Optional[str] = None,
    db: DatabaseSession = Depends(get_db),
    _: TokenDTO = Depends(jwt_guard)
) -> PaginatedResponseDTO[IDNamePairResponseDTO]:
    return get_id_name_pair_paginated_response(
        db=db,
        model=InterestModel,
        **pagination_params.model_dump(),
        ids=ids
    )