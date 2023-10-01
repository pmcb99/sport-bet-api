import json
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.server.data.sport import build_sport_filter
from app.server.database import get_db
from app.server.redis import redis_client

from app.server.schemas import sport_schema

router = APIRouter(
    prefix="/sports",
    tags=["sports"],
)

@router.get("/", response_model=List[sport_schema.Sport], tags=["sports"])
async def read_all_sports(name_regex: Optional[str]=None,
                          min_active_count: Optional[int]=None,
                          db: Session = Depends(get_db)):
    
    # check if we have a cached response
    cache_key = f"sports:all:{min_active_count}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        cached_json =  json.loads(cached_data)
        return [sport_schema.Sport(**json.loads(sport)) for sport in cached_json]

    filter_suffix = build_sport_filter(db, name_regex, min_active_count)
    query = text(f"""
        SELECT * 
        FROM sports
        {filter_suffix}
    """)    
    result = db.execute(query).all()
    sports = []
    for row in result:
        sports.append(
            sport_schema.Sport(
                id=row._mapping['id'],
                name=row._mapping['name'],
                slug=row._mapping['slug'],
                is_active=row._mapping['is_active'],
            )   
        )

    # cache the response
    json_sports = [sport.json() for sport in sports]
    redis_client.set(cache_key, json.dumps(json_sports), ex=60)

    return sports
