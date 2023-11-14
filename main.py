from fastapi import FastAPI, Request
from app.routes.users import user_router
from app.routes.communities import community_router
from app.routes.health import health_router
from app.routes.occupations import occupations_router
from app.routes.skills import skills_router
from app.routes.interests import interests_router

app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(community_router, prefix="/communities", tags=["communities"])
app.include_router(health_router, prefix="/health", tags=["health"])


# /occupations
app.include_router(occupations_router)

# /skills
app.include_router(skills_router)

# /interests
app.include_router(interests_router)


    
