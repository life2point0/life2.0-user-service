from .get_skills import get_skills_route
from .create_skill import create_skill_route
from fastapi import APIRouter

skills_router = APIRouter()
skills_router.include_router(get_skills_route, prefix="/skills")
skills_router.include_router(create_skill_route, prefix="/skills")