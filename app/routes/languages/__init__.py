from .get_languages import get_languages_route
from .create_language import create_language_route
from fastapi import APIRouter

languages_router = APIRouter()
languages_router.include_router(get_languages_route, prefix="/languages")
languages_router.include_router(create_language_route, prefix="/languages")