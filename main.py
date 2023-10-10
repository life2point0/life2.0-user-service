from fastapi import FastAPI, Request
from app.routes.users import user_router
from app.routes.communities import community_router
from app.routes.health import health_router

app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(community_router, prefix="/communities", tags=["communities"])
app.include_router(health_router, prefix="/health", tags=["health"])

    
