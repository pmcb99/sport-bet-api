from pydantic import BaseModel
from .event_schema import Event

class SportBase(BaseModel):
    name: str
    is_active: bool

class SportCreate(SportBase):
    pass

class SportPatch(SportBase):
    pass

class Sport(SportBase):
    id: int
    slug: str

    class Config:
        orm_mode = False
