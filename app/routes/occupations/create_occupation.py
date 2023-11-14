from fastapi import APIRouter, Depends, HTTPException
from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO
from app.models.occupation import OccupationModel
from app.database import DatabaseSession, get_db
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
import logging
from common.dto import TokenDTO
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

create_occupation_route = APIRouter()

@create_occupation_route.post('', response_model=IDNamePairResponseDTO, description='Create Occupation')
async def get_occupations(
    data: IDNamePairRequestDTO, 
    db: DatabaseSession = Depends(get_db),
    _: TokenDTO = Depends(jwt_guard)
):
    try:
        occupation = OccupationModel(**data.model_dump())
        db.add(occupation)
        db.commit()
        db.refresh(occupation)
        return IDNamePairResponseDTO.model_validate(occupation)
    except SQLAlchemyError as e:
        db.rollback()
        handle_sqlalchemy_error(e)
    except BaseException as e:
        db.rollback()
        raise HTTPException(status_code=500)
