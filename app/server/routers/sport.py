from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.server.data.sport import get_sport_by_id, get_sport_by_name_or_slug, insert_sport, update_sport_by_id
from app.server.database import get_db

from app.server.schemas import sport_schema
from app.utils.slug import get_slug

router = APIRouter(
    prefix="/sport",
    tags=["sport"],
)

@router.post("/", response_model=sport_schema.Sport)
async def create_sport(sport: sport_schema.SportCreate, db: Session = Depends(get_db)):
    """Create a new sport. Note a design decision has been taken to base the slug on the name, rather than have the user provide it."""
    new_slug = get_slug(sport.name)
    
    if get_sport_by_name_or_slug(db, sport.name):
        raise HTTPException(status_code=400, detail="Please provide a unique sport name")
    
    # sport inserted into DB using raw SQL execution
    result = insert_sport(db, sport.name, new_slug, sport.is_active)
    
    inserted_sport_model = sport_schema.Sport(
        id=result._mapping['id'],
        name=result._mapping['name'],
        is_active=result._mapping['is_active'],
        slug=result._mapping['slug']
    )
    return inserted_sport_model 

@router.patch("/{sport_id}", response_model=sport_schema.Sport)
async def update_sport(sport_id: str, sport: sport_schema.SportPatch, db: Session = Depends(get_db)):
    """Update a sport based on ID"""

    sport_item = get_sport_by_id(db, sport_id)
    if not sport_item:
        raise HTTPException(status_code=400, detail="Sport not found")
        
    new_slug = get_slug(sport.name)
    result = update_sport_by_id(db, sport_id, sport.name, new_slug, sport.is_active)
    
    updated_sport_model = sport_schema.Sport(
        id=result._mapping['id'],
        name=result._mapping['name'],
        is_active=result._mapping['is_active'],
        slug=result._mapping['slug']
    )
    return updated_sport_model
