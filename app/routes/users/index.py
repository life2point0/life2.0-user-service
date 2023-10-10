from fastapi import APIRouter, HTTPException, Header, Depends, Request
from jose import jwt
from pydantic import BaseModel, ValidationError
import requests
from app.constants import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, COMETCHAT_BASE_URL, COMETCHAT_KEY
from app.database import get_db, DatabaseSession
from app.models import UserModel, PlaceModel
from keycloak import KeycloakAdmin, KeycloakGetError, KeycloakError
from .dto import TokenDTO, UserPartialDTO, UserSignupDTO, JoinCommunityDTO
import logging
import json
from sqlalchemy import UUID

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

# TODO: Remove need for this. Use a locally stored key
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

def get_user_by_user_id(db: DatabaseSession, user_id: str):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is not None:
        return user.as_dict()
    return get_keycloak_user(user_id)

def create_cometchat_user(user: UserPartialDTO):
    phoneNumber = f"+{user.phone_country_code}" + user.phone_number if user.phone_country_code else user.phone_number
    try:
        res = requests.post(
            f"{COMETCHAT_BASE_URL}/users",
            headers={
                "ApiKey": COMETCHAT_KEY
            },
            json={
                "name": user.first_name,
                "uid": user.id,
                "metadata": {
                    "@private": {
                        "contactNumber": phoneNumber,
                        "email": user.email
                    }
                }
            }
        )
        return res.json()
    except HTTPException as e:
        logging.error(e)
        raise e

def add_user_to_cometchat_group(user_id: str, group_id: str):
    print('add_user_to_cometchat_group', user_id, group_id, {
                "participants": [user_id]
            })
    try:
        res = requests.post(
            f"{COMETCHAT_BASE_URL}/groups/{group_id}/members",
            headers={
                "ApiKey": COMETCHAT_KEY
            },
            json={
                "participants": [user_id]
            }
        )
        return res.json()
    except HTTPException as e:
        logging.error(e)
        raise e
    
def update_place_attribute(existing_user, attribute_name, data_dict, db):
    if attribute_name in data_dict:
        existing_place = db.query(PlaceModel).filter(PlaceModel.id == data_dict[attribute_name]['id']).first()
        if existing_place:
            setattr(existing_user, attribute_name, existing_place)
        else:
            new_place = PlaceModel(**data_dict[attribute_name])
            setattr(existing_user, attribute_name, new_place)

@router.get("/me")
def get_current_user(token_data: TokenDTO = Depends(jwt_guard), db: DatabaseSession = Depends(get_db)) -> UserPartialDTO:
    return get_user_by_user_id(db, user_id=token_data.sub)


@router.put("/me")
def update_current_user(
        user_data: UserPartialDTO,
        token_data: TokenDTO = Depends(jwt_guard), 
        db: DatabaseSession = Depends(get_db)
    ) -> UserPartialDTO:
    user_id = token_data.sub
    keycloak_user = get_keycloak_user(user_id)
    if keycloak_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    existing_user: UserModel = db.query(UserModel).filter(UserModel.id == user_id).first()
    user: UserModel
    logging.info(existing_user)
    if existing_user is None:
        data_dict = user_data.model_dump()
        user = UserModel(**data_dict)
        setattr(user, 'id', keycloak_user['id'])
        setattr(user, 'email', keycloak_user['email'])
        setattr(user, 'first_name', keycloak_user['firstName'])
        setattr(user, 'last_name', keycloak_user['lastName'])
        update_place_attribute(user, 'place_of_origin', data_dict, db)
        update_place_attribute(user, 'current_location', data_dict, db)
        db.add(user)
        create_cometchat_user(user)
    else:    
        data_dict = user_data.model_dump()
        logging.info(data_dict)
        for key, value in data_dict.items():
            if value is not None and hasattr(existing_user, key) and not isinstance(value, dict):
                setattr(existing_user, key, value)
        update_place_attribute(existing_user, 'place_of_origin', data_dict, db)
        update_place_attribute(existing_user, 'current_location', data_dict, db)
        # TODO: Write similar logic for places previously lived
        user = existing_user
    db.commit()
    db.refresh(user)
    user_dict= {**user.as_dict(), "id": str(user.id)}
    create_cometchat_user(UserPartialDTO(**user_dict))
    return user_dict

@router.post("/signup")
async def signup(
        user_data: UserSignupDTO
    ):
    try:
        user_id = keycloak_admin.create_user({
            "firstName": user_data.first_name,
            "lastName": user_data.last_name,
            "email": user_data.email,
            "username": user_data.email,
            "enabled": True,
            "credentials": [
                {
                    "type": "password",
                    "value": user_data.password
                }
            ]
        })
    except KeycloakError as e:
        error_dict = json.loads(e.error_message.decode('utf-8'))
        error_message = error_dict.get('errorMessage', 'An unknown error occurred')
        raise HTTPException(e.response_code, detail=error_message)
    return UserPartialDTO(**get_keycloak_user(user_id))

@router.post('/me/communities')
def join_community(payload: JoinCommunityDTO, token_data: TokenDTO = Depends(jwt_guard)):
    return add_user_to_cometchat_group(token_data.sub, payload.community_id)