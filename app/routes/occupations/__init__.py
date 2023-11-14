from .get_occupations import get_occupations_route
from .create_occupation import create_occupation_route
from fastapi import APIRouter

occupations_router = APIRouter()
occupations_router.include_router(get_occupations_route, prefix="/occupations", tags=["occupations"])
occupations_router.include_router(create_occupation_route, prefix="/occupations", tags=["occupations"])
