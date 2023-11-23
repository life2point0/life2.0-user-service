from .get_communities import get_communities_route
from .create_community import create_community_route
from .patch_community import patch_community_route
from fastapi import APIRouter

communities_router = APIRouter()
communities_router.include_router(get_communities_route, prefix="/communities")
communities_router.include_router(create_community_route, prefix="/communities")
communities_router.include_router(patch_community_route, prefix="/communities/{community_id}")