from fastapi import HTTPException
from sqlalchemy import case
from sqlalchemy.orm import Session as DatabaseSession
from typing import Type, List, Optional
from app.models import BaseModel  # Ensure you have the correct import path

def get_multi_rows(
    db: DatabaseSession,
    Model: Type[BaseModel],
    values: Optional[List[str]] = None,
    strict: Optional[bool] = False,
    sort_by_values: Optional[bool] = False
) -> List[BaseModel]:
    if values is not None:
        query = db.query(Model).filter(Model.id.in_(values))
        
        # Apply sorting if sort_by_values is True
        if sort_by_values:
            order_preservation = case(
                {str_id: index for index, str_id in enumerate(values)},
                value=Model.id
            )
            query = query.order_by(order_preservation)
        
        rows = query.all()

        # If strict mode is on, ensure all values have corresponding rows
        if strict and len(rows) != len(values):
            missing_values = set(values) - {str(row.id) for row in rows}
            raise HTTPException(
                status_code=400, 
                detail=f"Some {Model.__tablename__} were not recognized: {missing_values}"
            )

        return rows
    return None
