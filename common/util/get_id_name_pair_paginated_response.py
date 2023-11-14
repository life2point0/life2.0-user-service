from fastapi import HTTPException
from common.dto import IDNamePairResponseDTO, PaginatedResponseDTO
from typing import Optional, Type
from app.database import DatabaseSession;
import logging
from sqlalchemy import case
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
from app.database import BaseModel
from sqlalchemy.sql.expression import func

logging.basicConfig(level=logging.DEBUG) 


def get_id_name_pair_paginated_response(
    db: DatabaseSession,
    model: Type[BaseModel],
    per_page: Optional[int] = 0,
    page_number: Optional[int] = 0,
    ids: Optional[str] = None,
    query: Optional[str] = None
) -> PaginatedResponseDTO[IDNamePairResponseDTO]:
    try:
        db_query = db.query(model)
        if ids:
            id_list = ids.split(',')
            ordering = case(
                {id_value: index for index, id_value in enumerate(id_list)},
                value=model.id
            )
            db_query = query.filter(model.id.in_(id_list)).order_by(ordering)
        
        # TODO: Implement search vector
        if query:
            search_filter = model.name.ilike(f'%{query}%')
            db_query = db_query.filter(search_filter)
            db_query = db_query.order_by(func.length(model.name) - func.length(func.replace(model.name, query, '')))

        total = db_query.count()
        offset = page_number * per_page
        db_query = db_query.limit(per_page).offset(offset)
        
        data = db_query.all()
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