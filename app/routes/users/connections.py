from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.models import UserConnectionRequestModel, UserConnectionModel, UserModel
from app.dependencies import jwt_guard, jwt_optional
from common.dto import TokenDTO
from uuid import UUID
from .dto import CreateUserConnectionRequestDTO
from uuid import uuid4
from common.util import handle_sqlalchemy_error, create_one_to_one_stream_chat_channel
from common.dto import PaginationParams, PaginatedResponseDTO
from typing import Optional
from .dto import UserConnectionInfoDTO, CreateUserConnectionResponseDTO

# Import your SQLAlchemy models and database session setup here
# For example:
# from your_app.models import UserConnectionRequestModel, UserModel, get_db_session

user_connections_routes = APIRouter()

# FastAPI route to create a connection request and auto-approve it
@user_connections_routes.post("")
def create_connection_request(
    user_id: str,
    request_data: CreateUserConnectionRequestDTO,
    token_data: TokenDTO = Depends(jwt_guard),
    db: Session = Depends(get_db),
) -> CreateUserConnectionResponseDTO:
    if user_id != 'me' and user_id != str(token_data.sub): 
        raise HTTPException(403, "Forbidden")
    try:

        # Check if connection exists
        user_1, user_2 = sorted([token_data.sub, request_data.user_id], key=lambda x: str(x))
        user_connection = db.query(UserConnectionModel).filter(UserConnectionModel.user_id == user_1 and UserConnectionModel.connected_user_id == user_2).first()

        if (user_connection is None):

            # Create the connection request with auto-approval
            user_connection_request = UserConnectionRequestModel(
                id=uuid4(),
                requester_user_id=token_data.sub,
                requested_user_id=request_data.user_id,
                status="ACCEPTED"  # TODO: Implement request approval
            )

            # Create the connection
            user_connection = UserConnectionModel(
                user_id=token_data.sub,
                connected_user_id=request_data.user_id,
                connection_request=user_connection_request,
            )

            db.add(user_connection_request)
            db.add(user_connection)
            db.commit()

        channel = create_one_to_one_stream_chat_channel(user_1, user_2)
        return CreateUserConnectionResponseDTO(channel_id=channel.id)

    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)



@user_connections_routes.get("")
def get_user_connections(
    user_id: str,
    pagination_params: PaginationParams = Depends(),
    token_data: TokenDTO = Depends(jwt_optional),
    db: Session = Depends(get_db),
) -> PaginatedResponseDTO[UserConnectionInfoDTO]:
    if (user_id == 'me' and token_data.sub is None):
       raise HTTPException(403, "Forbidden")
    try:
        query_user_id = token_data.sub if user_id == 'me' else user_id
        page_number = pagination_params.page_number or 0
        per_page = pagination_params.per_page or 10
        print(query_user_id)
        query = db.query(UserModel).join(
            UserConnectionModel, 
            ((UserModel.id == UserConnectionModel.connected_user_id) & (UserConnectionModel.user_id == query_user_id)) |
            ((UserModel.id == UserConnectionModel.user_id) & (UserConnectionModel.connected_user_id == query_user_id))
        ).filter(
            UserModel.id != query_user_id
        ).offset(
            page_number * per_page
        ).limit(
            per_page
        )
        connected_users = query.offset(page_number * per_page).limit(per_page).all()
        return PaginatedResponseDTO[UserConnectionInfoDTO](
            data=connected_users,
            per_page=per_page,
            page_number=page_number,
            total=query.count()
        )
    except SQLAlchemyError as e:
        handle_sqlalchemy_error(e)
