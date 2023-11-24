from fastapi import APIRouter, Depends, HTTPException, Depends
from common.dto import IDNamePairRequestDTO, IDNamePairResponseDTO
from app.models.interest import InterestModel
from app.database import DatabaseSession, get_db
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
import logging
from typing import Type
from app.database import BaseModel
from uuid import UUID

logging.basicConfig(level=logging.DEBUG) 

create_interest_route = APIRouter()

def create_id_name_pair_row(
        db: DatabaseSession,
        Model: Type[BaseModel],
        name: str,
        created_by: UUID
    ):
    try:
        normalized_name = ' '.join(name.split()).title()
        row = db.query(Model).filter(Model.name == normalized_name).first()
        if row is None:
            row = Model(name=normalized_name, created_by_user_id=created_by)
            db.add(row)
            db.commit()
            db.refresh(row)
        return row
    except SQLAlchemyError as e:
        db.rollback()
        handle_sqlalchemy_error(e)
    except BaseException as e:
        db.rollback()
        raise HTTPException(status_code=500)