from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.settings import AppSettings
from app.database import get_db, DatabaseSession
from app.models import UserModel, CommunityModel, UserConnectionModel, NotificationModel
from keycloak import KeycloakGetError, KeycloakError
from .dto import UserUpdateDTO, UserPartialDTO, UserSignupDTO, JoinCommunityDTO, ThirdPartyTokenResponseDTO, UserConnectionInfoDTO, PatchUserParams
import logging
import json
from stream_chat import StreamChat
from app.dependencies import jwt_guard
from common.dto import TokenDTO
from .user_photos import user_photo_routes
from app.models import OccupationModel, SkillModel, LanguageModel, InterestModel
from common.util import get_multi_rows, get_place, get_places, handle_sqlalchemy_error, datetime_from_epoch_ms, keycloak_openid, keycloak_admin, get_or_create_file_objects
from typing import Callable
from uuid import UUID
from datetime import datetime, timedelta
from requests import HTTPError
from app.routes.communities.dto import CommunityDTO
from .connections import user_connections_routes
from firebase_admin import messaging
from .util import find_top_matching_users
from common.dto.notifications import NotificationType, NewUserJoinedNotification
from .notifications import user_notifications_routes

logging.basicConfig(level=logging.DEBUG) 
router = APIRouter()

stream_chat = StreamChat(api_key=AppSettings.STREAM_ACCESS_KEY_ID, api_secret=AppSettings.STREAM_SECRET_ACCESS_KEY)

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


def get_user_by_user_id(db: DatabaseSession, user_id: str, exclude_relations: bool = False):
    options = [] if exclude_relations else [
        joinedload(UserModel.place_of_origin),
        joinedload(UserModel.current_place),
        joinedload(UserModel.past_places),
        joinedload(UserModel.occupations),
        joinedload(UserModel.interests),
        joinedload(UserModel.skills),
        joinedload(UserModel.languages),
        joinedload(UserModel.photos),
    ]
    user = (
        db.query(UserModel)
            .options(*options)
            .filter(UserModel.id == user_id)
            .first()
    )

    if user is None:
        return get_keycloak_user(user_id), False
    
    return user, True


def upsert_streamchat_user(user: UserModel):
    try:
        user_data = {
            "id": str(user.id),
            "name": f"{user.first_name} {user.last_name}",
            "role": "user",
        }
        if user.photos is not None and len(user.photos) > 0:
            photo = user.photos[0]
            if photo is not None:   
                user_data['image'] = user.photos[0].url
        stream_chat.update_user(user_data)
    except HTTPError as e:
        logging.error(e)
        raise e


def replace_user_relations(db: DatabaseSession, user_id: UUID, user_dict: dict):
    user_dict['occupations'] = get_multi_rows(db, OccupationModel, values=user_dict['occupations'], strict=True)
    user_dict['skills'] = get_multi_rows(db, SkillModel, values=user_dict['skills'], strict=True)
    user_dict['interests'] = get_multi_rows(db, InterestModel, values=user_dict['interests'], strict=True)
    user_dict['languages'] = get_multi_rows(db, LanguageModel, values=user_dict['languages'], strict=True)
    user_dict['current_place'] = get_place(db, place_id=user_dict['current_place'])
    user_dict['place_of_origin'] = get_place(db, place_id=user_dict['place_of_origin'])
    user_dict['past_places'] = get_places(db, place_ids=user_dict['past_places'])
    user_dict['photos'] = get_or_create_file_objects(db, user_id=user_id, file_ids=user_dict['photos'])

def is_user_a_connection(db: DatabaseSession, current_user_id: UUID, target_user_id: UUID) -> bool:
    # Check if there's a connection between the current user and the target user
    connection = (
        db.query(UserConnectionModel)
        .filter(
            (
                (UserConnectionModel.user_id == current_user_id)
                & (UserConnectionModel.connected_user_id == target_user_id)
            )
            | (
                (UserConnectionModel.user_id == target_user_id)
                & (UserConnectionModel.connected_user_id == current_user_id)
            )
        )
        .first()
    )
    
    # If a connection exists, the users are connected
    return connection is not None


def notify_matching_users(db: DatabaseSession, user_id: UUID, notification_type: NotificationType):

    user, _ = get_user_by_user_id(db, user_id)
    if (notification_type == NotificationType.NEW_USER_JOINED): 
        notif_template = NewUserJoinedNotification(user)
    else:
        return
    
    top_matches = find_top_matching_users(db, user_id)
    user_ids = [match['user_id'] for match in top_matches]
    users = [
        NotificationModel(
            data=json.loads(notif_template.model_dump_json(by_alias=True)),
            target_user_id=user_id
        ) 
    for user_id in user_ids]
    logging.debug(users)
    db.add_all(users)
    db.commit()

    chat_users = [stream_chat.get_devices(user_id) for user_id in user_ids]
    device_tokens = []

    for chat_user in chat_users:
        for device in chat_user["devices"]:
            device_tokens.append(device["id"])


    message = messaging.MulticastMessage(
        tokens = device_tokens,
        android = notif_template.android
    )
    messaging.send_multicast(message)
    print(device_tokens)

@router.get("/me")
def get_current_user(token_data: TokenDTO = Depends(jwt_guard), db: DatabaseSession = Depends(get_db)) -> UserPartialDTO:
    user, is_profile_created = get_user_by_user_id(db, user_id=token_data.sub)
    res = UserPartialDTO.model_validate(user)
    res.is_profile_created = is_profile_created
    return res

@router.get("/{user_id}")
def get_current_user(user_id: UUID, token_data: TokenDTO = Depends(jwt_guard), db: DatabaseSession = Depends(get_db)):
    user, _ = get_user_by_user_id(db, user_id)
    if user_id == token_data.sub:
        return UserPartialDTO.model_validate(user) 
    else:
        user_dto = UserConnectionInfoDTO.model_validate(user)
        user_dto.is_connection = is_user_a_connection(db, token_data.sub, user_id)
        return user_dto


@router.patch("/me")
def update_current_user(
        user_data: UserUpdateDTO,
        background_tasks: BackgroundTasks,
        query_params: PatchUserParams = Depends(),
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

        print(user_dict)
        is_email_changed = user_dict.get('email') is not None
        is_name_changed = user_dict['first_name'] is not None or user_dict['last_name'] is not None
        is_photos_changed = user_dict['photos'] is not None

        replace_user_relations(db, token_data.sub, user_dict)
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
        if query_params.notification_type is not None:
            background_tasks.add_task(notify_matching_users, db, user_id, query_params.notification_type)
            # notify_matching_users(db, user_id, query_params.notification_type)
        user_dto = UserPartialDTO.model_validate(user)
        user_dto.is_profile_created = not is_new
        return user_dto
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
def join_community(payload: JoinCommunityDTO, token_data: TokenDTO = Depends(jwt_guard), db: DatabaseSession = Depends(get_db)):
    user_id = token_data.sub
    community_id = payload.community_id
    channel = stream_chat.channel("community", str(payload.community_id))
    try:
        user = db.query(UserModel).options(joinedload(UserModel.communities)).filter(UserModel.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        community = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
        if community is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.communities.append(community)
        channel.add_members([str(token_data.sub)])
        db.commit()
    except SQLAlchemyError as e:
        if isinstance(e, IntegrityError):
            raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="You are already a member of this community")
        else:
            channel.remove_members([str(token_data.sub)])
            handle_sqlalchemy_error(e)
    except HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e.response.json()))
    


@router.get('/me/communities')
def list_user_communities(token_data: TokenDTO = Depends(jwt_guard), db: DatabaseSession = Depends(get_db)):
    user = db.query(UserModel).options(joinedload(UserModel.communities)).filter(UserModel.id == token_data.sub).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return [CommunityDTO.model_validate(community) for community in user.communities]


@router.get('/me/tokens')
def get_tokens(token_data: TokenDTO = Depends(jwt_guard)) -> ThirdPartyTokenResponseDTO:
    now = datetime.utcnow()
    token = stream_chat.create_token(
        str(token_data.sub), 
        iat = now,
        exp = now + timedelta(hours=1)
    )
    return ThirdPartyTokenResponseDTO(stream_chat=token)

@router.get('/me/tokens/fcm')
def set_fcm_token(token_data: TokenDTO = Depends(jwt_guard)):
    deviceRes = stream_chat.get_devices(token_data.sub)
    tokens = [str(device['id']) for device in deviceRes['devices']]
    message = messaging.MulticastMessage(
        tokens = [str(device['id']) for device in deviceRes['devices'] if 'id' in device and device['id']],
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                channel_id='new-matching-user',
                icon='https://bulma.io/images/placeholders/96x96.png',
                title='Tabrez just joined Life 2.0'
            ),
            collapse_key='new-matching-user'
        )
    )
    messaging.send_multicast(message)
    return tokens
    


router.include_router(user_photo_routes, prefix="/me/photos")
router.include_router(user_connections_routes, prefix="/{user_id}/connections", tags=["connections"])
router.include_router(user_notifications_routes, prefix="/me/notifications", tags=["notifications"])
