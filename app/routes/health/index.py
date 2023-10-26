import logging
from fastapi import APIRouter, Depends
from app.database import get_db
from sqlalchemy import text
from app.database import DatabaseSession

logging.basicConfig(level=logging.DEBUG) 
router = APIRouter()

@router.get("")
def community_list(db: DatabaseSession = Depends(get_db)):
    db.execute(text('SELECT 1')).fetchall()
    return { "status": "alive" }