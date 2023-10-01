from decimal import Decimal
import json
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.server.data.selection import build_selection_filter
from app.server.database import get_db
from app.server.redis import redis_client

from app.server.schemas import selection_schema

router = APIRouter(
    prefix="/selections",
    tags=["selections"],
)

@router.get("/", response_model=List[selection_schema.Selection], tags=["selections"])
async def read_all_selections(name_regex: Optional[str]=None,
                              filter_by_outcome: Optional[str]=None,
                              filter_by_event: Optional[str]=None,
                              min_price: Optional[Decimal]=None,
                              max_price: Optional[Decimal]=None,
                              db: Session = Depends(get_db)):

    # check if we have a cached response if no filters are applied
    all_filters = [name_regex, filter_by_outcome, filter_by_event, min_price, max_price]
    if not any(all_filters):
        cache_key = "selections:all"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            cached_json =  json.loads(cached_data)
            return [selection_schema.Selection(**json.loads(selection)) for selection in cached_json]
    
    filter_suffix = build_selection_filter(name_regex, filter_by_outcome, filter_by_event, min_price, max_price)

    query = text(f"""
        SELECT * 
        FROM selections
        {filter_suffix}
    """)
    result = db.execute(query).all()
    selections = []
    for row in result:
        selections.append(
            selection_schema.Selection(
                id=row._mapping['id'],
                name=row._mapping['name'],
                outcome=row._mapping['outcome'],
                price=row._mapping['price'],
                event_id=row._mapping['event_id'],
                is_active=row._mapping['is_active'],
            )
        )

    if not any(all_filters):
        # cache the response
        json_selections = [selection.json() for selection in selections]
        redis_client.set(cache_key, json.dumps(json_selections), ex=60)

    return selections