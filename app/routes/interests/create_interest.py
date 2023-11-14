from fastapi import APIRouter, Depends, HTTPException, Depends
from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO
from app.models.interest import InterestModel
from app.database import DatabaseSession, get_db
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
import logging
from common.dto import TokenDTO
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

create_interest_route = APIRouter()

@create_interest_route.post('', response_model=IDNamePairResponseDTO, description="Get Interests")
async def get_interests(
    data: IDNamePairRequestDTO, 
    db: DatabaseSession = Depends(get_db),
    _: TokenDTO = Depends(jwt_guard)
):
    try:
        interest = InterestModel(**data.model_dump())
        db.add(interest)
        db.commit()
        db.refresh(interest)
        return IDNamePairResponseDTO.model_validate(interest)
    except SQLAlchemyError as e:
        db.rollback()
        handle_sqlalchemy_error(e)
    except BaseException as e:
        db.rollback()
        raise HTTPException(status_code=500)
