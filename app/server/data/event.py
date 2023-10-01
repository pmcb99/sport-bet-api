import datetime
from fastapi import HTTPException
from sqlalchemy import text
from app.server.data.sport import get_sport_by_id
from app.server.models.enums import EventStatus, EventType
from app.server.schemas import event_schema
from sqlalchemy.orm import Session

from app.utils.slug import get_slug


def get_event_by_id(db: Session, event_id: str):
    query = text(f"SELECT * FROM events WHERE id = {event_id}")
    query_result = db.execute(query).all()
    return query_result if query_result else None


def get_event_by_name_or_slug(db: Session, name: str):
    slug = get_slug(name)
    query = text(f"SELECT * FROM events WHERE name = '{name}' OR slug = '{slug}'")
    return db.execute(query).all()


def insert_event(db: Session, event: event_schema.EventCreate):
    # check if sport exists
    if get_sport_by_id(db, event.sport_id) is None:
        raise HTTPException(status_code=400, detail="Sport does not exist")
    
    if event.actual_start and event.actual_start < event.scheduled_start:
        raise HTTPException(status_code=400, detail="Actual start time cannot be before scheduled start time")
    
    event_type = EventType.PREPLAY
    if event.actual_start and event.actual_start > datetime.datetime.utcnow():
        event_type = EventType.INPLAY
    
    if event.status == EventStatus.PENDING and event.actual_start:
        raise HTTPException(status_code=400, detail="Cannot have pending event that has started")

    insert_stmt = text(
        "INSERT INTO events (name, slug, is_active, event_type, \
                       sport_id, status, scheduled_start, actual_start) \
                       VALUES (:name, :slug, :is_active, :event_type, :sport_id, \
                       :status, :scheduled_start, :actual_start) RETURNING *"
    )
    result = db.execute(
        insert_stmt,
        {
            "name": event.name,
            "slug": get_slug(event.name),
            "is_active": event.is_active,
            "event_type": event_type,
            "sport_id": event.sport_id,
            "status": event.status,
            "scheduled_start": event.scheduled_start,
            "actual_start": event.actual_start,
        },
    ).fetchone()
    db.commit()
    return result


def update_event_by_id(db: Session, event_id: str, event: event_schema.EventPatch):

    # can do more checking here to ensure the times make sense but we'll assume this is handled 
    event_type = EventType.INPLAY if event.actual_start else EventType.PREPLAY

    update_stmt = text(
        "UPDATE events SET name = :name, slug = :slug, is_active = :is_active, event_type = :event_type, sport_id = :sport_id, \
        status = :status, scheduled_start = :scheduled_start, actual_start = :actual_start WHERE id = :id RETURNING *"
    )
    result = db.execute(
        update_stmt,
        {
            "id": event_id,
            "name": event.name,
            "slug": get_slug(event.name),
            "is_active": event.is_active,
            "event_type": event_type,
            "sport_id": event.sport_id,
            "status": event.status,
            "scheduled_start": event.scheduled_start,
            "actual_start": event.actual_start,
        },
    ).fetchone()
    db.commit()
    return result

# can use a single query here if we want to avoid the extra db call
# but I favour evaluating the logic in python for readability until analysis shows this is a bottleneck
def update_event_if_selections_inactive(db, event_id: int):
    # count number of active selections for this event
    query = text(f"SELECT COUNT(*) FROM selections WHERE event_id = {event_id} AND is_active = True")
    query_result = db.execute(query).all()
    active_selections_count = query_result[0][0]
    if active_selections_count == 0:
        # if no active selections, update the event to is_active = False
        update_stmt = text(f"UPDATE events SET is_active = False WHERE id = {event_id} RETURNING *")
        db.execute(update_stmt)
        db.commit()

def build_event_filter(db: Session,
                       name_regex: str,
                       min_active_count: int,
                       scheduled_start_time_utc: str,
                       scheduled_end_time_utc: str,
                       actual_start_time_utc: str,
                       actual_end_time_utc: str):
    where_clauses = []
    if name_regex:
        where_clauses.append(f"name LIKE '{name_regex}'")
    
    if min_active_count:
        event_ids = text(f"SELECT event_id FROM selections WHERE is_active = true GROUP BY event_id HAVING COUNT(is_active) >= {min_active_count}")
        result = db.execute(event_ids).all()
        event_ids = [str(row[0]) for row in result]
        where_clauses.append(f"id IN ({','.join(event_ids)})")
    
    if scheduled_start_time_utc:
        where_clauses.append(f"scheduled_start >= '{scheduled_start_time_utc}'")
    if scheduled_end_time_utc:
        where_clauses.append(f"scheduled_start <= '{scheduled_end_time_utc}'")
    if actual_start_time_utc:
        where_clauses.append(f"actual_start >= '{actual_start_time_utc}'")
    if actual_end_time_utc:
        where_clauses.append(f"actual_start <= '{actual_end_time_utc}'")

        
    where_clause = " AND ".join(where_clauses)

    filter_suffix = "WHERE " + where_clause if where_clause else ""