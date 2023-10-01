import json
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.server.data.event import build_event_filter
from app.server.database import get_db
from app.server.redis import redis_client

from app.server.schemas import event_schema

router = APIRouter(
    prefix="/events",
    tags=["events"],
)

@router.get("/", response_model=List[event_schema.Event], tags=["events"])
async def read_all_events(name_regex: Optional[str]=None,
                          min_active_count: Optional[int]=None,
                          scheduled_start_time_utc: Optional[str]=None,
                          scheduled_end_time_utc: Optional[str]=None,
                          actual_start_time_utc: Optional[str]=None,
                          actual_end_time_utc: Optional[str]=None,
                          db: Session = Depends(get_db)):

    filter_values = [name_regex, min_active_count, scheduled_start_time_utc, scheduled_end_time_utc, actual_start_time_utc, actual_end_time_utc] 
    if not any(filter_values):
        # check if we have a cached response
        cache_key = "events:all"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            cached_json =  json.loads(cached_data)
            return [event_schema.Event(**json.loads(event)) for event in cached_json]

    filter_suffix = build_event_filter(db, name_regex, min_active_count, scheduled_start_time_utc, scheduled_end_time_utc, actual_start_time_utc, actual_end_time_utc)

    query = text(f"""
        SELECT * 
        FROM events
        {filter_suffix}
    """)    
    result = db.execute(query).all()
    events = []
    for row in result:
        events.append(
            event_schema.Event(
                id=row._mapping['id'],
                name=row._mapping['name'],
                slug=row._mapping['slug'],
                is_active=row._mapping['is_active'],
                sport_id=row._mapping['sport_id'],
                scheduled_start=row._mapping['scheduled_start'],
                actual_start=row._mapping['actual_start'],
                event_type=row._mapping['event_type'],
                status=row._mapping['status'],
            )   
        )

    # set cache value
    redis_client.set(cache_key, json.dumps([event.json() for event in events]), ex=60)

    return events