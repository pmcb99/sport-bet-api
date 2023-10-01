from typing import Optional
from sqlalchemy import text
from app.server.schemas import sport_schema
from sqlalchemy.orm import Session

from app.utils.slug import get_slug


def get_sport_by_id(db: Session, sport_id: str):
    query = text(f"SELECT * FROM sports WHERE id = {sport_id}")
    query_result = db.execute(query).all()
    return query_result if query_result else None

def get_sport_by_name_or_slug(db: Session, name: str):
    slug = get_slug(name)
    query = text(f"SELECT * FROM sports WHERE name = '{name}' OR slug = '{slug}'")
    return db.execute(query).all()

def insert_sport(db: Session, name: str, slug: str, is_active: bool):
    insert_stmt = text("INSERT INTO sports (name, slug, is_active) VALUES (:name, :slug, :is_active) RETURNING *")
    result = db.execute(insert_stmt, {'name': name, 'slug': slug, 'is_active': is_active}).fetchone()
    db.commit()
    return result

def update_sport_by_id(db: Session, sport_id: str, name: str, slug: str, is_active: bool):
    update_stmt = text("UPDATE sports SET name = :name, slug = :slug, is_active = :is_active WHERE id = :id RETURNING *")
    result = db.execute(update_stmt, {'id': sport_id, 'name': name, 'slug': slug, 'is_active': is_active}).fetchone()
    db.commit()
    return result


# can use a single query here if we want to avoid the extra db call
# but I favour evaluating the logic in python for readability until analysis shows this is a bottleneck
def update_sport_if_events_inactive(db, sport_id: int):
    # count number of active events for this sport
    query = text(f"SELECT COUNT(*) FROM events WHERE sport_id = {sport_id} AND is_active = True")
    query_result = db.execute(query).all()
    active_events_count = query_result[0][0]
    if active_events_count == 0:
        # if no active events, update the sport to is_active = False
        update_stmt = text(f"UPDATE sports SET is_active = False WHERE id = {sport_id}")
        db.execute(update_stmt)
        db.commit()


def build_sport_filter(db: Session,
                       name_regex: Optional[str]=None,
                       min_active_count: Optional[int]=None):
    where_clauses = []
    if name_regex:
        where_clauses.append(f"name LIKE '{name_regex}'")
    
    if min_active_count:
        sport_ids = text(f"SELECT sport_id FROM events WHERE is_active = true GROUP BY sport_id HAVING COUNT(is_active) >= {min_active_count}")
        result = db.execute(sport_ids).all()
        event_ids = [str(row[0]) for row in result]
        where_clauses.append(f"id IN ({','.join(event_ids)})")

        
    where_clause = " AND ".join(where_clauses)

    filter_suffix = "WHERE " + where_clause if where_clause else ""
    
    return filter_suffix

