from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.models.interest import InterestModel
from app.database import DatabaseSession, get_db;
from common.dto import PaginatedResponseDTO, IDNamePairResponseDTO
import logging
from sqlalchemy import case
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
from common.dto import TokenDTO
from app.dependencies import jwt_guard
from common.dto import TokenDTO
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

get_interests_route = APIRouter()

@get_interests_route.get('', tags=['Interest List'])
def get_interests(
    db: DatabaseSession = Depends(get_db),
    per_page: Optional[int] = None,
    page_number: Optional[int] = 0,
    ids: Optional[str] = None,
    _: TokenDTO = Depends(jwt_guard)
) -> PaginatedResponseDTO[IDNamePairResponseDTO]:
    try:
        query = db.query(InterestModel)
        if ids:
            id_list = ids.split(',')
            ordering = case(
                {id_value: index for index, id_value in enumerate(id_list)},
                value=InterestModel.id
            )
            query = query.filter(InterestModel.id.in_(id_list)).order_by(ordering)
        total = query.count()
        if per_page is not None:
            offset = page_number * per_page
            query = query.limit(per_page).offset(offset)
        interests = query.all()
        return PaginatedResponseDTO(
            data=interests,
            page_number=page_number,
            per_page=(per_page if per_page is not None else total),
            total=total
        )
    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)
    except BaseException as e:
        raise HTTPException(status_code=500)