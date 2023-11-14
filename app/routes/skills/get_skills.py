from fastapi import APIRouter, Depends, HTTPException
from common.dto import IDNamePairResponseDTO
from typing import Optional, List
from app.models.skill import SkillModel
from app.database import DatabaseSession, get_db;
from common.dto import PaginatedResponseDTO
import logging
from sqlalchemy import case
from sqlalchemy.exc import SQLAlchemyError
from common.util import handle_sqlalchemy_error
from common.dto import TokenDTO
from app.dependencies import jwt_guard

logging.basicConfig(level=logging.DEBUG) 

get_skills_route = APIRouter()

@get_skills_route.get('', tags=['Skill List'])
def get_skills(
    db: DatabaseSession = Depends(get_db),
    per_page: Optional[int] = None,
    page_number: Optional[int] = 0,
    ids: Optional[str] = None,
    _: TokenDTO = Depends(jwt_guard)
) -> PaginatedResponseDTO[IDNamePairResponseDTO]:
    try:
        query = db.query(SkillModel)
        if ids:
            id_list = ids.split(',')
            ordering = case(
                {id_value: index for index, id_value in enumerate(id_list)},
                value=SkillModel.id
            )
            query = query.filter(SkillModel.id.in_(id_list)).order_by(ordering)
        total = query.count()
        if per_page is not None:
            offset = page_number * per_page
            query = query.limit(per_page).offset(offset)
        skills = query.all()
        return PaginatedResponseDTO(
            data=skills,
            page_number=page_number,
            per_page=(per_page if per_page is not None else total),
            total=total
        )
    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)
    except BaseException as e:
        raise HTTPException(status_code=500)