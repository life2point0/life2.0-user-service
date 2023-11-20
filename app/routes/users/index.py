from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.settings import AppSettings
from app.database import get_db, DatabaseSession
from app.models import UserModel, PlaceModel
from keycloak import KeycloakAdmin, KeycloakGetError, KeycloakError, KeycloakOpenID
from .dto import UserUpdateDTO, UserPartialDTO, UserSignupDTO, JoinCommunityDTO, RefreshTokenRequestDTO, UserLoginRequestDTO, UserLoginResponseDTO, RefreshTokenRequestDTO
import logging
import json
from stream_chat import StreamChat
from app.dependencies import jwt_guard
from common.dto import TokenDTO
from .user_photos import user_photo_routes
from app.models import OccupationModel, SkillModel, LanguageModel, InterestModel, FileModel
from common.util import get_multi_rows, get_place, get_places, handle_sqlalchemy_error, datetime_from_epoch_ms, keycloak_openid, keycloak_admin
from typing import List, Callable
from uuid import UUID
from datetime import datetime, timedelta
from requests import HTTPError

logging.basicConfig(level=logging.DEBUG) 
router = APIRouter()

streamChat = StreamChat(api_key=AppSettings.STREAM_ACCESS_KEY_ID, api_secret=AppSettings.STREAM_SECRET_ACCESS_KEY)

def get_keycloak_user(user_id: str):
    try:
        user = keycloak_admin.get_user(user_id)
        if user:
            return user
    except KeycloakGetError as e:
        logging.error(f"An error occurred: {e}")
        raise HTTPException(status_code=e.response_code, detail=e.response_body.decode('utf-8'))


def update_keycloak_user(user: UserModel) -> Callable:
    # Save the original user data for rollback purposes
    original_user_data = {
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name
    }

    try:
        keycloak_user_data = {
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name
        }

        # Update the user in Keycloak
        keycloak_admin.update_user(user_id=user.id, payload=keycloak_user_data)
        
        # No exception means update was successful
        # Return a rollback function that can be called if needed
        def rollback():
            keycloak_admin.update_user(user_id=user.id, payload=original_user_data)
            print("Rollback successful.")
            
        return rollback

    except KeycloakError as e:
        logging.error(f"Error updating user in Keycloak: {e}")
        raise e


def get_user_by_user_id(db: DatabaseSession, user_id: str):
    user = (
        db.query(UserModel)
            .options(
                joinedload(UserModel.place_of_origin),
                joinedload(UserModel.current_place),
                joinedload(UserModel.past_locations),
                joinedload(UserModel.occupations),
                joinedload(UserModel.interests),
                joinedload(UserModel.skills),
                joinedload(UserModel.languages),
                joinedload(UserModel.photos),
            )
            .filter(UserModel.id == user_id)
            .first()
    )

    if user is None:
        return get_keycloak_user(user_id)
    
    return user


def upsert_streamchat_user(user: UserModel):
    try:
        user_data = {
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}",
            "role": "user",
        }
        if user.photos is not None:
            photo = user.photos[0]
            if photo is not None:   
                user_data['image'] = user.photos[0].url
        streamChat.update_user(user_data)
    except HTTPError as e:
        logging.error(e)
        raise e
    
def get_photo_objects(db: DatabaseSession, photos_ids: List[str]):
    if photos_ids is None: 
        return None
    try:
        photos = db.query(FileModel).filter(FileModel.id.in_(photos_ids)).all()
        new_photo_ids = set([str(photo_id) for photo_id in photos_ids]) - set([str(photo.id) for photo in photos])
        for photo_id in new_photo_ids:
            photos.append(FileModel(
                id=UUID(photo_id),
                bucket=AppSettings.FILE_UPLOAD_BUCKET,
                file_extension='jpg',
                folder='user-photos',
                cdn_host=AppSettings.FILE_UPLOAD_CDN
            ))
        return photos
    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)
    

def replace_user_relations(db: DatabaseSession, user_dict: dict):
    user_dict['occupations'] = get_multi_rows(db, OccupationModel, values=user_dict['occupations'], strict=True)
    user_dict['skills'] = get_multi_rows(db, SkillModel, values=user_dict['skills'], strict=True)
    user_dict['interests'] = get_multi_rows(db, InterestModel, values=user_dict['interests'], strict=True)
    user_dict['languages'] = get_multi_rows(db, LanguageModel, values=user_dict['languages'], strict=True)
    user_dict['current_place'] = get_place(db, place_id=user_dict['current_place'])
    user_dict['place_of_origin'] = get_place(db, place_id=user_dict['place_of_origin'])
    user_dict['past_locations'] = get_places(db, place_ids=user_dict['past_locations'])
    user_dict['photos'] = get_photo_objects(db, photos_ids=user_dict['photos'])

@router.get("/me")
def get_current_user(token_data: TokenDTO = Depends(jwt_guard), db: DatabaseSession = Depends(get_db)) -> UserPartialDTO:
    return get_user_by_user_id(db, user_id=token_data.sub)

@router.patch("/me")
def update_current_user(
        user_data: UserUpdateDTO,
        token_data: TokenDTO = Depends(jwt_guard), 
        db: DatabaseSession = Depends(get_db)
    ) -> UserPartialDTO:
    user_id = token_data.sub
    try:
        user: UserModel = db.query(UserModel).filter(UserModel.id == user_id).first()
        is_new = user is None
        if is_new:
            keycloak_user = get_keycloak_user(user_id)
            if keycloak_user is None:
                raise HTTPException(status_code=404, detail='User not found')
            user = UserModel(
                id = keycloak_user['id'],
                email = keycloak_user['email'],
                first_name = keycloak_user['firstName'],
                last_name = keycloak_user['lastName'],
                created_at = datetime_from_epoch_ms(keycloak_user['createdTimestamp'])
            )
            db.add(user)

        user_dict = user_data.model_dump()

        is_email_changed = user_dict['email'] is not None
        is_name_changed = user_dict['first_name'] is not None or user_dict['last_name'] is not None
        is_photos_changed = user_dict['photos'] is not None

        replace_user_relations(db, user_dict)
        for key, value in user_dict.items():
            if value is not None and hasattr(user, key) and not isinstance(value, dict):
                setattr(user, key, value)

        if is_name_changed or is_email_changed:
            try: 
                rollback_keycloak_user = update_keycloak_user(user)
            except KeycloakError as e:
                raise HTTPException(e.response_code, str(e))
        if is_new or is_name_changed or is_photos_changed:
            try:
                upsert_streamchat_user(user)
            except HTTPError as e:
                if rollback_keycloak_user is not None:
                    rollback_keycloak_user(user)
                raise HTTPException(e.response.status_code, str(e))
        
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)


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
    user_dict = get_keycloak_user(user_id)
    return UserPartialDTO(**user_dict)

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
    now = datetime.utcnow()
    token = streamChat.create_token(
        token_data.sub, 
        iat = now,
        exp = now + timedelta(hours=1)
    )
    return {
        "streamChat": token
    }


router.include_router(user_photo_routes, prefix="/me/photos")
