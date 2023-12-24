from os import getenv
from dotenv import load_dotenv
load_dotenv()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    KEYCLOAK_URL: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_REALM: str
    STREAM_ACCESS_KEY_ID: str
    STREAM_SECRET_ACCESS_KEY: str
    FILE_UPLOAD_BUCKET: str
    FILE_UPLOAD_CDN: str
    FILE_UPLOAD_URL_VALIDITY: int
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_ENDPOINT: str = "https://s3.me-central-1.amazonaws.com"
    AWS_DEFAULT_REGION: str = "me-central-1"
    GOOGLE_MAPS_API_KEY: str
    FIREBASE_KEY_JSON: str

    class Config:
        env_file = ".env"

AppSettings = Settings()


