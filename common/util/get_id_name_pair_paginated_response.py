from fastapi import HTTPException
from common.dto import IDNamePairResponseDTO, PaginatedResponseDTO
from typing import Optional, Type
from app.database import DatabaseSession;
import logging
from sqlalchemy import case
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
from app.database import BaseModel

logging.basicConfig(level=logging.DEBUG) 


def get_id_name_pair_paginated_response(
    db: DatabaseSession,
    model: Type[BaseModel],
    per_page: Optional[int] = None,
    page_number: Optional[int] = 0,
    ids: Optional[str] = None,
    query: Optional[str] = None
) -> PaginatedResponseDTO[IDNamePairResponseDTO]:
    try:
        query = db.query(model)
        if ids:
            id_list = ids.split(',')
            ordering = case(
                {id_value: index for index, id_value in enumerate(id_list)},
                value=model.id
            )
            query = query.filter(model.id.in_(id_list)).order_by(ordering)
        total = query.count()
        if per_page is not None:
            offset = page_number * per_page
            query = query.limit(per_page).offset(offset)
        data = query.all()
        return PaginatedResponseDTO(
            data=data,
            page_number=page_number,
            per_page=(per_page if per_page is not None else total),
            total=total
        )
    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)
    except BaseException as e:
        raise HTTPException(status_code=500)