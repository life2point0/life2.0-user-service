from os import getenv
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = getenv('DATABASE_URL')
KEYCLOAK_URL = getenv('KEYCLOAK_URL')
KEYCLOAK_CLIENT_ID = getenv('KEYCLOAK_CLIENT_ID')
KEYCLOAK_CLIENT_SECRET = getenv('KEYCLOAK_CLIENT_SECRET')
KEYCLOAK_REALM = getenv('KEYCLOAK_REALM')