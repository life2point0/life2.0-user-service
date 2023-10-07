from fastapi import APIRouter, HTTPException, Header, Depends
from jose import jwt
from pydantic import BaseModel, ValidationError
import requests
from app.constants import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET
from app.database import get_db, DatabaseSession
from app.models import UserModel
from keycloak import KeycloakAdmin, KeycloakGetError
from .dto import TokenDTO, UserPartialDTO
import logging

logging.basicConfig(level=logging.DEBUG) 
router = APIRouter()

keycloak_admin = KeycloakAdmin(
    server_url=KEYCLOAK_URL,
    realm_name=KEYCLOAK_REALM,
    client_id=KEYCLOAK_CLIENT_ID,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    verify=True,
)

keycloak_admin.token

def get_key_from_jwks(kid):
    jwks_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
    jwks = requests.get(jwks_url).json()
    for jwk in jwks['keys']:
        if jwk['kid'] == kid:
            return jwk
    raise Exception("Key not found")

def get_keycloak_user(user_id: str):
    try:
        user = keycloak_admin.get_user(user_id)
        if user:
            return user
    except KeycloakGetError as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=e.response_code, detail=e.response_body.decode('utf-8'))

def jwt_guard(authorization: str = Header(...)) -> TokenDTO:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    
    token = authorization[len(prefix):]
    try:
        header = jwt.get_unverified_header(token)
        kid = header['kid']
        public_key = get_key_from_jwks(kid)

        decoded_token = jwt.decode(token, public_key, audience="account")
        return TokenDTO(**decoded_token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
        
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    except ValidationError as e:
        raise HTTPException(status_code=401, detail="Token payload validation failed")

@router.get("/me")
def protected_route(token_data: TokenDTO = Depends(jwt_guard), db: DatabaseSession = Depends(get_db)) -> UserPartialDTO:
    user_id = token_data.sub
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        keycloak_user = get_keycloak_user(user_id)
        print(keycloak_user)
        return UserPartialDTO()
    else:
        return user.dict()
