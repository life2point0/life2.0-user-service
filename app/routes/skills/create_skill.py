from fastapi import APIRouter, Depends, HTTPException
from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO
from app.models.skill import SkillModel
from app.database import DatabaseSession, get_db
from sqlalchemy.exc import SQLAlchemyError
from common.util import create_id_name_pair_row
import logging
from common.dto import TokenDTO
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

create_skill_route = APIRouter()

@create_skill_route.post('', response_model=IDNamePairResponseDTO, description='Create Skill')
async def get_skills(
    data: IDNamePairRequestDTO, 
    db: DatabaseSession = Depends(get_db),
    token_data: TokenDTO = Depends(jwt_guard)
):
    return create_id_name_pair_row(db, SkillModel, created_by=token_data.sub, name=data.name)
