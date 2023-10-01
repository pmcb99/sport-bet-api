from fastapi import HTTPException
from sqlalchemy import text
from app.server.data.event import get_event_by_id
from app.server.schemas import selection_schema
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


def get_selection_by_id(db: Session, selection_id: str):
    query = text(f"SELECT * FROM selections WHERE id = '{selection_id}'")
    return db.execute(query).all()

def insert_selection(db: Session, selection: selection_schema.SelectionCreate):
    # check if event exists
    event = get_event_by_id(db, selection.event_id)
    if event is None:
        return None  # or return a custom error indicating event not found
    
    try:
        # Here, assuming that 'id' is the primary key column of 'selections' table
        insert_stmt = text(
            "INSERT INTO selections (name, event_id, price, is_active, outcome) "
            "VALUES (:name, :event_id, :price, :is_active, :outcome) RETURNING *"
        )
        
        result = db.execute(
            insert_stmt,
            {
                "name": selection.name,
                "event_id": selection.event_id,
                "price": str(selection.price),
                "is_active": selection.is_active,
                "outcome": selection.outcome,
            }
        ).fetchone()  # get the returned record
        db.commit()
        
        return result  # return the id of the newly inserted selection
    except SQLAlchemyError as e:
        # Handle the SQLAlchemy error if insertion fails
        print(e)  # for logging purpose, replace with actual logging in production
        db.rollback()
        return None  # or return a custom error indicating insertion failure


def update_selection_by_id(db: Session, selection_id: str, selection: selection_schema.SelectionPatch):
    update_stmt = text(
        "UPDATE selections SET name = :name, is_active = :is_active, event_id = :event_id,\
        price = :price, is_active = :is_active, outcome= :outcome WHERE id = :id RETURNING *"
    )
    result = db.execute(
        update_stmt,
        {
            "id": selection_id,
            "name": selection.name,
            "event_id": selection.event_id,
            "price": str(selection.price),
            "is_active": selection.is_active,
            "outcome": selection.outcome,
        }
    ).fetchone()  # get the returned record
    db.commit()
    
    return result


def build_selection_filter(name_regex: str=None,
                                filter_by_outcome: str=None,
                                filter_by_event: str=None,
                                min_price: str=None,
                                max_price: str=None):
    where_clauses = []
    if name_regex:
        where_clauses.append(f"name LIKE '{name_regex}'")

    if filter_by_outcome:
        where_clauses.append(f"outcome = '{filter_by_outcome}'")
    
    if filter_by_event:
        where_clauses.append(f"event_id = '{filter_by_event}'")
    
    if min_price:
        where_clauses.append(f"price >= '{min_price}'")
    
    if max_price:
        where_clauses.append(f"price <= '{max_price}'")
    
    where_clause = " AND ".join(where_clauses)

    filter_suffix = "WHERE " + where_clause if where_clause else ""
    return filter_suffix