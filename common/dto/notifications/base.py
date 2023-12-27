from pydantic import create_model
from enum import Enum
from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic.generics import GenericModel
from firebase_admin import messaging
from uuid import UUID
from ..base import BaseDTO
import json

# Notification Action Types
class NotificationType(str, Enum):
    NEW_USER_JOINED = "NEW_USER_JOINED"

class NotificationActionType(str, Enum):
    SEND_MESSAGE = "SEND_MESSAGE"
    VIEW_PROFILE = "VIEW_PROFILE"
    DISMISS = "DISMISS"

# Generic Type Variable for Action Data
T = TypeVar('T')

# Generic Notification Action Class
class NotificationAction(BaseDTO, GenericModel, Generic[T]):
    action_type: NotificationActionType
    action_data: T

class BaseNotificationAction(BaseDTO):
    action_label: str = 'Take Action'

# Specific Action Data Structures
class SendMessageActionData(BaseNotificationAction):
    user_id: UUID
    message: str
    action_label: str = 'Say Hi'

class ViewProfileActionData(BaseNotificationAction):
    user_id: UUID
    action_label: str = 'View Profile'

class DismissActionData(BaseNotificationAction):
    action_label: str = 'Dismiss'

# Base Notification Template
class BaseNotificationTemplate(BaseDTO):
    notification_type: str
    title: str
    body: str
    icon: Optional[str] = None
    actions: List[NotificationAction] = []

    class Config:
        use_enum_values = True

    # Platform-specific getters
    @property
    def android(self) -> messaging.AndroidConfig:
        android_notification = messaging.AndroidNotification(
            title=self.title,
            body=self.body,
            icon=self.icon
        )
        android_data: Dict[str, Any] = {
            'actions': json.dumps([action.model_dump_json(by_alias=True) for action in self.actions]),
        }
        return messaging.AndroidConfig(notification=android_notification, data=android_data)

    @property
    def ios(self) -> messaging.APNSConfig:
        aps = messaging.Aps(alert=messaging.ApsAlert(title=self.title, body=self.body), sound="default")
        ios_data: Dict[str, Any] = {action.action_type: action.action_data.dict() for action in self.actions}
        return messaging.APNSConfig(payload=messaging.APNSPayload(aps=aps, custom_data=ios_data))

    @property
    def web(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "body": self.body,
            "icon": self.icon,
            "data": {action.action_type: action.action_data.dict() for action in self.actions}
        }

    @property
    def in_app(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "message": self.body,
            "icon_url": self.icon,
            "actions": {action.action_type: action.action_data.dict() for action in self.actions}
        }
