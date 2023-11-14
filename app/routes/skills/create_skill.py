from fastapi import APIRouter, Depends, HTTPException
from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO
from app.models.skill import SkillModel
from app.database import DatabaseSession, get_db
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
import logging
from common.dto import TokenDTO
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

create_skill_route = APIRouter()

@create_skill_route.post('', response_model=IDNamePairResponseDTO, tags=['Create Skill'])
async def get_skills(
    data: IDNamePairRequestDTO, 
    db: DatabaseSession = Depends(get_db),
    _: TokenDTO = Depends(jwt_guard)
):
    try:
        skill = SkillModel(**data.model_dump())
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return IDNamePairResponseDTO.model_validate(skill)
    except SQLAlchemyError as e:
        db.rollback()
        handle_sqlalchemy_error(e)
    except BaseException as e:
        db.rollback()
        raise HTTPException(status_code=500)
