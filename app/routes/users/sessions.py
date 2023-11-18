from fastapi import APIRouter, HTTPException
from keycloak import KeycloakError
from .dto import RefreshTokenRequestDTO, UserLoginRequestDTO, UserLoginResponseDTO, RefreshTokenRequestDTO
import logging
from common.util import keycloak_openid

logging.basicConfig(level=logging.DEBUG) 
sessions_router = APIRouter()

@sessions_router.post("", description="Login")
def login(req_data: UserLoginRequestDTO) -> UserLoginResponseDTO:
    try:
        return keycloak_openid.token(req_data.username, req_data.password)
    except KeycloakError as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=e.response_code, detail=e.response_body.decode('utf-8'))

@sessions_router.delete("", description="Logout")
def logout(req_data: RefreshTokenRequestDTO):
    try:
        keycloak_openid.logout(req_data.refresh_token)
    except KeycloakError as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=e.response_code, detail=e.response_body.decode('utf-8'))
    
@sessions_router.post("/token", description="Refresh Token")
def refresh_token(req_data: RefreshTokenRequestDTO) -> UserLoginResponseDTO:
    try:
        return keycloak_openid.refresh_token(req_data.refresh_token)
    except KeycloakError as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=e.response_code, detail=e.response_body.decode('utf-8'))