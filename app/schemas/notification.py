from datetime import datetime
from pydantic import BaseModel, ConfigDict

class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    priority: str
    message: str
    resource_type: str | None
    resource_id: int | None
    is_read: bool
    created_at: datetime

    # Helper property for UI styling based on priority
    @property
    def color(self) -> str:
        return "red" if self.priority == "urgent" else "blue"

    model_config = ConfigDict(from_attributes=True)