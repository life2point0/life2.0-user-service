from fastapi import APIRouter, Depends
from common.dto import IDNamePairResponseDTO, PaginationParams, PaginatedResponseDTO, TokenDTO
from common.util import get_id_name_pair_paginated_response
from typing import Optional
from app.models.language import LanguageModel
from app.database import DatabaseSession, get_db;
import logging
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

get_languages_route = APIRouter()

@get_languages_route.get('', description='Language List')
def get_languages(
    pagination_params: PaginationParams = Depends(),
    ids: Optional[str] = None,
    db: DatabaseSession = Depends(get_db),
    _: TokenDTO = Depends(jwt_guard)
) -> PaginatedResponseDTO[IDNamePairResponseDTO]:
    return get_id_name_pair_paginated_response(
        db=db,
        model=LanguageModel,
        **pagination_params.model_dump(),
        ids=ids
    )