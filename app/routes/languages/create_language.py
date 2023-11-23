from fastapi import APIRouter, Depends, Depends
from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO
from app.models.language import LanguageModel
from app.database import DatabaseSession, get_db
from common.util import create_id_name_pair_row
import logging
from common.dto import TokenDTO
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

create_language_route = APIRouter()

@create_language_route.post('', response_model=IDNamePairResponseDTO, description="Get Languages")
async def get_languages(
    data: IDNamePairRequestDTO, 
    db: DatabaseSession = Depends(get_db),
    token_data: TokenDTO = Depends(jwt_guard)
):
    return create_id_name_pair_row(db, LanguageModel, created_by=token_data.sub, name=data.name)
