from fastapi import APIRouter, Depends, HTTPException
from common.dto import IDNamePairResponseDTO
from typing import Optional, List
from app.models.occupation import OccupationModel
from app.database import DatabaseSession, get_db;
from common.dto import PaginatedResponseDTO, TokenDTO
import logging
from sqlalchemy import case
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

get_occupations_route = APIRouter()

@get_occupations_route.get('', tags=['Occupation List'])
def get_occupations(
    db: DatabaseSession = Depends(get_db),
    per_page: Optional[int] = None,
    page_number: Optional[int] = 0,
    ids: Optional[str] = None,
    _: TokenDTO = Depends(jwt_guard)
) -> PaginatedResponseDTO[IDNamePairResponseDTO]:
    try:
        query = db.query(OccupationModel)
        if ids:
            id_list = ids.split(',')
            ordering = case(
                {id_value: index for index, id_value in enumerate(id_list)},
                value=OccupationModel.id
            )
            query = query.filter(OccupationModel.id.in_(id_list)).order_by(ordering)
        total = query.count()
        if per_page is not None:
            offset = page_number * per_page
            query = query.limit(per_page).offset(offset)
        occupations = query.all()
        return PaginatedResponseDTO(
            data=occupations,
            page_number=page_number,
            per_page=(per_page if per_page is not None else total),
            total=total
        )
    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)
    except BaseException as e:
        raise HTTPException(status_code=500)