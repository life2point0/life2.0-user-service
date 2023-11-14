from fastapi import APIRouter, Depends, HTTPException, Depends
from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO
from app.models.interest import InterestModel
from app.database import DatabaseSession, get_db
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
import logging
from typing import Type
from app.database import BaseModel

logging.basicConfig(level=logging.DEBUG) 

create_interest_route = APIRouter()

def create_id_name_pair_row(
        db: DatabaseSession,
        model: Type[BaseModel],
        name: str,
    ):
    try:
        row = db.query(model).filter(model.name == name).first()
        if row is None:
            row = model(name=name)
            db.add(row)
            db.commit()
            db.refresh(row)
        return IDNamePairResponseDTO.model_validate(row)
    except SQLAlchemyError as e:
        db.rollback()
        handle_sqlalchemy_error(e)
    except BaseException as e:
        db.rollback()
        raise HTTPException(status_code=500)