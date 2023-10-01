from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.server.data.event import get_event_by_id, get_event_by_name_or_slug, insert_event, update_event_by_id
from app.server.data.sport import update_sport_if_events_inactive
from app.server.database import get_db

from app.server.schemas import event_schema
from app.utils.slug import get_slug

router = APIRouter(
    prefix="/event",
    tags=["event"],
)

@router.post("/", response_model=event_schema.Event)
async def create_event(event: event_schema.EventCreate, db: Session = Depends(get_db)):
    """Create a new event. Note a design decision has been taken to base the slug on the name, rather than have the user provide it."""
    new_slug = get_slug(event.name)
    
    if get_event_by_name_or_slug(db, event.name):
        raise HTTPException(status_code=400, detail="event already registered")
    
    # event inserted into DB using raw SQL execution
    result = insert_event(db, event)
    
    inserted_event_model = event_schema.Event(
        id=result._mapping["id"],
        name=result._mapping["name"],
        slug=result._mapping["slug"],
        is_active=result._mapping["is_active"],
        sport_id=result._mapping["sport_id"],
        status=result._mapping["status"],
        scheduled_start=result._mapping["scheduled_start"],
        event_type=result._mapping["event_type"],
        actual_start=result._mapping["actual_start"],
    )
    return inserted_event_model 

@router.patch("/{event_id}", response_model=event_schema.Event)
async def update_event(event_id: str, event: event_schema.EventPatch, db: Session = Depends(get_db)):
    """Update a event based on ID"""

    event_item = get_event_by_id(db, event_id)
    if not event_item:
        raise HTTPException(status_code=400, detail="event not found")
    
    if get_event_by_name_or_slug(db, event.name):
        raise HTTPException(status_code=400, detail="Please provide a unique event name")
        
    result = update_event_by_id(db, event_id, event)
    
    updated_event_model = event_schema.Event(
        id=result._mapping["id"],
        name=result._mapping["name"],
        slug=result._mapping["slug"],
        is_active=result._mapping["is_active"],
        sport_id=result._mapping["sport_id"],
        event_type=result._mapping["event_type"],
        status=result._mapping["status"],
        scheduled_start=result._mapping["scheduled_start"],
        actual_start=result._mapping["actual_start"],
    )
    # purposefully not doing this in create function because it wouldnt really make sense since  
    # we could have created an active sport with no events, or an active event with no selections
    if not updated_event_model.is_active:
        # if so, update all bets with this selection_id to is_active = False
        update_sport_if_events_inactive(db, event.sport_id)

    return updated_event_model