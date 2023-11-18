from fastapi import HTTPException, Header
from pydantic import ValidationError
from common.dto import TokenDTO
from jose import jwt
from app.settings import AppSettings
import requests
from functools import lru_cache

@lru_cache(maxsize=16)
def get_key_from_jwks(kid):
    jwks_url = f"{AppSettings.KEYCLOAK_URL}/realms/{AppSettings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    jwks = requests.get(jwks_url).json()
    for jwk in jwks['keys']:
        if jwk['kid'] == kid:
            return jwk
    raise HTTPException(status_code=401, detail="Token signed with an unknown key")

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
