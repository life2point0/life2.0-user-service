from fastapi import FastAPI
from app.routes.users import user_router

app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["users"])
