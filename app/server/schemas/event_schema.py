from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import datetime
from app.server.models.enums import EventStatus, EventType
from .selection_schema import Selection

class EventBase(BaseModel):
    name: str
    is_active: bool
    sport_id: int 
    status: EventStatus
    scheduled_start: datetime.datetime
    actual_start: Optional[datetime.datetime]=None


class EventCreate(EventBase):
    pass

class EventPatch(EventBase):
    pass

class Event(EventBase):
    id: int
    slug: str
    event_type: EventType

    class Config:
        orm_mode = False