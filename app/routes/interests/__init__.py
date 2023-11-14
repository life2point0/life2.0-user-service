from .get_interests import get_interests_route
from .create_interest import create_interest_route
from fastapi import APIRouter

interests_router = APIRouter()
interests_router.include_router(get_interests_route, prefix="/interests")
interests_router.include_router(create_interest_route, prefix="/interests")