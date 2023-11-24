from fastapi import APIRouter, Depends
from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO
from app.models.occupation import OccupationModel
from app.database import DatabaseSession, get_db
from common.util import create_id_name_pair_row
import logging
from common.dto import TokenDTO
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

create_occupation_route = APIRouter()

@create_occupation_route.post('', response_model=IDNamePairResponseDTO, description='Create Occupation')
async def get_occupations(
    data: IDNamePairRequestDTO, 
    db: DatabaseSession = Depends(get_db),
    token_data: TokenDTO = Depends(jwt_guard)
):
    return IDNamePairResponseDTO.model_validate(create_id_name_pair_row(db, OccupationModel, created_by=token_data.sub, name=data.name))
