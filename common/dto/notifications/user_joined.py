from app.models import UserModel
from .base import (
    NotificationAction, 
    SendMessageActionData, 
    NotificationActionType, 
    ViewProfileActionData, 
    BaseNotificationTemplate,
    NotificationType
)
from firebase_admin import messaging
from uuid import UUID


# NewUserJoined Notification Template
class NewUserJoinedNotification(BaseNotificationTemplate):
    user_id: UUID
    def __init__(self, user: UserModel, **kwargs):
        actions = [
            NotificationAction[SendMessageActionData](
                action_type=NotificationActionType.SEND_MESSAGE,
                action_data=SendMessageActionData(user_id=user.id, message="Hi there!")
            ),
            NotificationAction[ViewProfileActionData](
                action_type=NotificationActionType.VIEW_PROFILE,
                action_data=ViewProfileActionData(user_id=user.id)
            )
        ]
        super().__init__(
            notification_type=NotificationType.NEW_USER_JOINED,
            title=f"{user.first_name} just joined Life 2.0!",
            body=f"{user.first_name} {user.last_name} has just joined us. There's so much you have in common with them, we thought we'd let you know!",
            icon=user.photos[0].url if user.photos[0] else None,
            actions=actions,
            user_id=user.id,
            **kwargs
        )

    @property
    def android(self) -> messaging.AndroidConfig:
        android_notification = super().android
        android_notification.data['userId'] = str(self.user_id)
        android_notification.data['notificationType'] = str(self.notification_type)
        print (android_notification.data)
        return android_notification
