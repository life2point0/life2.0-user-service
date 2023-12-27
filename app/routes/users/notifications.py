from fastapi import APIRouter, HTTPException, Depends
from keycloak import KeycloakError
from .dto import NotificationDTO, MarkAllNotificationsReadDTO
import logging
from common.util import keycloak_openid
from common.dto import PaginationParams, PaginatedResponseDTO, TokenDTO
from common.dto.notifications import BaseNotificationTemplate
from app.models import NotificationModel
from app.database import get_db, DatabaseSession
from app.dependencies import jwt_guard
from sqlalchemy import text, update
import json

logging.basicConfig(level=logging.DEBUG) 
user_notifications_routes = APIRouter()

@user_notifications_routes.get("", description="Get recent user notifications")
def get_user_notifications(
    pagination_params: PaginationParams = Depends(),
    token_data: TokenDTO = Depends(jwt_guard),
    db: DatabaseSession = Depends(get_db)
) -> PaginatedResponseDTO[NotificationDTO]:
    query = (
        db.query(NotificationModel)
        .filter(NotificationModel.target_user_id == token_data.sub)
        .order_by(text('created_at DESC'))
        .offset(pagination_params.per_page * pagination_params.page_number)
        .limit(pagination_params.per_page)
    )
    notifications = query.all()
    count = query.count()
    return PaginatedResponseDTO(
        per_page=pagination_params.per_page,
        total=count,
        page_number=pagination_params.page_number,
        data=[{
            **notification.data, 
            'created_at': notification.created_at,
            'is_read': notification.is_read
        } for notification in notifications]
    )


@user_notifications_routes.put("/read-status", description="Mark all notifications read")
def get_user_notifications(
    _: MarkAllNotificationsReadDTO,
    token_data: TokenDTO = Depends(jwt_guard),
    db: DatabaseSession = Depends(get_db)
):
    db.execute(
        update(NotificationModel)
        .where(NotificationModel.target_user_id == token_data.sub)
        .values(is_read=True)
    )
    db.commit()
    return {}