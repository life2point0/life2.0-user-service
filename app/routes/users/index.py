from fastapi import APIRouter, HTTPException, Depends
from app.constants import (
    KEYCLOAK_URL, 
    KEYCLOAK_REALM, 
    KEYCLOAK_CLIENT_ID, 
    KEYCLOAK_CLIENT_SECRET, 
    STREAM_ACCESS_KEY_ID, 
    STREAM_SECRET_ACCESS_KEY, 
    MEDIA_UPLOAD_BUCKET, 
    S3_ENDPOINT, 
    AWS_DEFAULT_REGION,
    MEDIA_UPLOAD_URL_VALIDITY
)
from app.database import get_db, DatabaseSession
from app.models import UserModel, PlaceModel
from keycloak import KeycloakAdmin, KeycloakGetError, KeycloakError
from .dto import UserPartialDTO, UserSignupDTO, JoinCommunityDTO, PhotoUploadUrlDTO
import logging
import json
from stream_chat import StreamChat
import datetime
import boto3
from uuid import uuid4
from app.dependencies import jwt_guard
from common.dto import TokenDTO
from .user_photos import user_photo_routes

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

streamChat = StreamChat(api_key=STREAM_ACCESS_KEY_ID, api_secret=STREAM_SECRET_ACCESS_KEY)

def get_keycloak_user(user_id: str):
    try:
        user = keycloak_admin.get_user(user_id)
        if user:
            return user
    except KeycloakGetError as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=e.response_code, detail=e.response_body.decode('utf-8'))

def get_user_by_user_id(db: DatabaseSession, user_id: str):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is not None:
        return user.as_dict()
    return get_keycloak_user(user_id)

def create_streamchat_user(user: UserPartialDTO):
    try:
        user_data = {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "role": "user"
        }
        streamChat.update_user(user_data)
    except HTTPException as e:
        logging.error(e)
        raise e

def update_place_attribute(user, attribute_name, data_dict, db):
    if attribute_name in data_dict and data_dict[attribute_name] is not None:
        existing_place = db.query(PlaceModel).filter(PlaceModel.id == data_dict[attribute_name]['id']).first()
        if existing_place:
            setattr(user, attribute_name, existing_place)
        else:
            new_place = PlaceModel(**data_dict[attribute_name])
            setattr(user, attribute_name, new_place)

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
    logging.info('[Existing User]', existing_user)
    data_dict = user_data.model_dump()
    data_dict['occupations'] = None # TODO: Remove this
    data_dict['past_locations'] = None # TODO: Remove this
    if existing_user is None:
        user = UserModel(**data_dict)
        setattr(user, 'id', keycloak_user['id'])
        setattr(user, 'email', keycloak_user['email'])
        setattr(user, 'first_name', keycloak_user['firstName'])
        setattr(user, 'last_name', keycloak_user['lastName'])
        update_place_attribute(user, 'place_of_origin', data_dict, db)
        update_place_attribute(user, 'current_location', data_dict, db)
        db.add(user)
        logging.info('[User]', user.as_dict())
    else:    
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
    create_streamchat_user(UserPartialDTO(**user_dict))
    logging.info('[SUCCESS]')
    return UserPartialDTO(**user_dict)

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
    channel = streamChat.channel("community", payload.community_id)
    channel.add_members([token_data.sub])


@router.get('/me/communities')
def join_community(token_data: TokenDTO = Depends(jwt_guard)):
    filter_conditions = {
        "type": "community",
        "members": {"$in": [token_data.sub]}
    }
    sort = {"created_at": -1}
    response = streamChat.query_channels(filter_conditions, sort=sort)
    return response


@router.get('/me/tokens')
def join_community(token_data: TokenDTO = Depends(jwt_guard)):
    now = datetime.datetime.utcnow()
    token = streamChat.create_token(
        token_data.sub, 
        iat = now,
        exp = now + datetime.timedelta(hours=1)
    )
    return {
        "streamChat": token
    }

router.include_router(user_photo_routes, prefix="/me/photos", tags=["photos"])