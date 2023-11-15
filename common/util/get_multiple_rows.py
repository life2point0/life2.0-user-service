from fastapi import HTTPException
from app.database import DatabaseSession
from app.models import OccupationModel
from typing import Type, List, Optional
from app.database import BaseModel

def get_multi_rows(
    db: DatabaseSession,
    Model: Type[BaseModel],
    values: Optional[List[str]] = None,
    strict: Optional[bool] = False
):
    if values is not None: 
        rows = db.query(Model).filter(OccupationModel.id.in_(values)).all()
        if strict and len(values) is not len(rows):
            raise HTTPException(status_code=400, detail=f'Some {Model.__tablename__} were not recognized')
        return rows
    return None