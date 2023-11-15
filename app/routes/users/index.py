from fastapi import APIRouter, HTTPException, Depends
from app.constants import (
    KEYCLOAK_URL, 
    KEYCLOAK_REALM, 
    KEYCLOAK_CLIENT_ID, 
    KEYCLOAK_CLIENT_SECRET, 
    STREAM_ACCESS_KEY_ID, 
    STREAM_SECRET_ACCESS_KEY
)
from app.database import get_db, DatabaseSession
from app.models import UserModel, PlaceModel
from keycloak import KeycloakAdmin, KeycloakGetError, KeycloakError
from .dto import UserUpdateDTO, UserPartialDTO, UserSignupDTO, JoinCommunityDTO
import logging
import json
from stream_chat import StreamChat
import datetime
from app.dependencies import jwt_guard
from common.dto import TokenDTO
from .user_photos import user_photo_routes
from app.models import OccupationModel, SkillModel, LanguageModel, InterestModel
from common.util import get_multi_rows, get_place, get_places

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
            "id": str(user.id),
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
        user_data: UserUpdateDTO,
        token_data: TokenDTO = Depends(jwt_guard), 
        db: DatabaseSession = Depends(get_db)
    ) -> UserPartialDTO:
    user_id = token_data.sub
    keycloak_user = get_keycloak_user(user_id)
    if keycloak_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    existing_user: UserModel = db.query(UserModel).filter(UserModel.id == user_id).first()
    user: UserModel
    data_dict = user_data.model_dump()
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
        data_dict['occupations'] = get_multi_rows(db, OccupationModel, values=data_dict['occupations'], strict=True)
        data_dict['skills'] = get_multi_rows(db, SkillModel, values=data_dict['skills'], strict=True)
        data_dict['interests'] = get_multi_rows(db, InterestModel, values=data_dict['interests'], strict=True)
        data_dict['languages'] = get_multi_rows(db, LanguageModel, values=data_dict['languages'], strict=True)
        data_dict['current_location'] = get_place(db, place_id=data_dict['current_location'])
        data_dict['place_of_origin'] = get_place(db, place_id=data_dict['place_of_origin'])
        data_dict['past_locations'] = get_places(db, place_ids=data_dict['past_locations'])
        for key, value in data_dict.items():
            if value is not None and hasattr(existing_user, key) and not isinstance(value, dict):
                setattr(existing_user, key, value)
        # TODO: Write similar logic for places previously lived
        user = existing_user
    db.commit()
    db.refresh(user)
    res = UserPartialDTO.model_validate(user)
    create_streamchat_user(res)
    logging.info('[SUCCESS]')
    return res

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

router.include_router(user_photo_routes, prefix="/me/photos")