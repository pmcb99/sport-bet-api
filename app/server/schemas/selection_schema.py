
from decimal import Decimal
from pydantic import BaseModel, condecimal

from app.server.models.enums import SelectionOutcome

# assume this is the minimum price for a selection
MINIMUM_PRICE = Decimal('5.00')

class SelectionBase(BaseModel):
    name: str
    event_id: int
    price: condecimal(decimal_places=2, ge=MINIMUM_PRICE)
    is_active: bool
    outcome: SelectionOutcome


class SelectionCreate(SelectionBase):
    pass

class SelectionPatch(SelectionBase):
    pass


class Selection(SelectionBase):
    id: int

    class Config:
        orm_mode = True