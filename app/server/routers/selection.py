from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.server.data.event import get_event_by_id
from app.server.data.selection import get_selection_by_id, insert_selection, update_selection_by_id
from app.server.database import get_db
from app.server.data.event import update_event_if_selections_inactive

from app.server.schemas import selection_schema

router = APIRouter(
    prefix="/selection",
    tags=["selection"],
)

@router.post("/", response_model=selection_schema.Selection)
async def create_selection(selection: selection_schema.SelectionCreate, db: Session = Depends(get_db)):
    """Create a new selection. Note a design decision has been taken to base the slug on the name, rather than have the user provide it."""
    
    event_id = get_event_by_id(db, selection.event_id)  

    if not event_id:
        raise HTTPException(status_code=400, detail="Error inserting the selection or event does not exist")
    
     # Retrieve the selection from the DB including the ID using the appropriate method
    selection_record = insert_selection(db, selection)
    
    if not selection_record:
        raise HTTPException(status_code=404, detail="Inserted selection not found")
    
    # Construct the Selection object to return
    decimal_price = f"{selection_record.price:.2f}"
    inserted_selection_model = selection_schema.Selection(
        id=selection_record.id,
        name=selection_record.name,
        event_id=selection_record.event_id,
        is_active=selection_record.is_active,
        outcome=selection_record.outcome,
        price=Decimal(decimal_price)
    )
    
    return inserted_selection_model 

@router.patch("/{selection_id}", response_model=selection_schema.Selection)
async def update_selection(selection_id: str, selection: selection_schema.SelectionPatch, db: Session = Depends(get_db)):
    """Update a selection based on ID"""
    
    # check if event exists
    if get_event_by_id(db, selection.event_id) is None:
        raise HTTPException(status_code=400, detail="Event does not exist")

    selection_item = get_selection_by_id(db, selection_id)
    if not selection_item:
        raise HTTPException(status_code=400, detail="selection not found")
        
    inserted_selection = update_selection_by_id(db, selection_id, selection)
    
    updated_selection_model = selection_schema.Selection(
        id=inserted_selection.id,
        name=inserted_selection.name,
        event_id=inserted_selection.event_id,
        is_active=inserted_selection.is_active,
        outcome=inserted_selection.outcome,
        price=Decimal(str(inserted_selection.price))
    )
    
    # check if is_active has been updated to False
    # purposefully not doing this in create function because it wouldnt really make sense since  
    # we could have created an active sport with no events, or an active event with no selections
    if not updated_selection_model.is_active:
        # if so, update all bets with this selection_id to is_active = False
        update_event_if_selections_inactive(db, selection.event_id)

    return updated_selection_model