from fastapi import FastAPI
from app.routes.users import user_router, sessions_router
from app.routes.communities import communities_router
from app.routes.health import health_router
from app.routes.occupations import occupations_router
from app.routes.skills import skills_router
from app.routes.interests import interests_router
from app.routes.languages import languages_router
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from firebase_admin import credentials, initialize_app
from app.settings import AppSettings
import json


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

security_scheme = {
    "Bearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
}
def app_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="User Service",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = security_scheme
    openapi_schema["security"] = [{"Bearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = app_openapi

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
app.include_router(health_router, prefix="/health", tags=["health"])


app.include_router(communities_router, tags=["communities"])

# /occupations
app.include_router(occupations_router, tags=['occupations'])

# /skills
app.include_router(skills_router, tags=['skills'])

# /interests
app.include_router(interests_router, tags=['interests'])

# /languages
app.include_router(languages_router, tags=['languages'])

@app.on_event('startup')
def startup():
    # Initialize firebase
    creds = credentials.Certificate(json.loads(AppSettings.FIREBASE_KEY_JSON))
    initialize_app(creds)
