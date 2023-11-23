from fastapi import APIRouter, Depends, Depends
from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO
from app.models.interest import InterestModel
from app.database import DatabaseSession, get_db
from common.util import create_id_name_pair_row
import logging
from common.dto import TokenDTO
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

create_interest_route = APIRouter()

@create_interest_route.post('', response_model=IDNamePairResponseDTO, description="Get Interests")
async def get_interests(
    data: IDNamePairRequestDTO, 
    db: DatabaseSession = Depends(get_db),
    token_data: TokenDTO = Depends(jwt_guard)
):
    return create_id_name_pair_row(db, InterestModel, name=data.name, created_by=token_data.sub)
