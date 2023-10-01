import uuid
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.server.app import app
from app.server.database import Base, get_db


DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)  # Create all tables

client = TestClient(app)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


import uuid
from fastapi.testclient import TestClient
from app.server.app import app
from app.server.database import get_db

client = TestClient(app)


def test_create_event():
    unique_name = "Event_" + str(uuid.uuid4())
    response = client.post(
        "/event",
        json={
            "name": unique_name,
            "is_active": True,
            "sport_id": 1,
            "status": "STARTED",
            "scheduled_start": "2023-09-29T12:00:00",
            "event_type": "INPLAY",
            "actual_start": "2023-09-29T12:05:00",
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == unique_name

    response = client.post(
        "/event",
        json={
            "name": unique_name,
            "is_active": True,
            "sport_id": 1,
            "status": "STARTED",
            "scheduled_start": "2023-09-29T12:00:00",
            "event_type": "INPLAY",
            "actual_start": "2023-09-29T12:05:00",
        },
    )
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "event already registered"

    response = client.post(
        "/event",
        json={},
    )
    assert response.status_code == 422, response.text


def test_update_event():
    # First, you need to create an event, then try to update it.
    # Here, we are directly going with an ID, make sure the ID exists in your test database or adjust accordingly.
    event_id = 4
    unique_name = "Arsenal v Chelsea" + str(uuid.uuid4())
    response = client.patch(
        f"/event/{event_id}",
        json={
            "name": unique_name,
            "is_active": True,
            "event_type": "PREPLAY",
            "sport_id": 6,
            "status": "ENDED",
            "scheduled_start": "2023-10-03T14:30:00Z",
            "actual_start": "2023-11-03T14:30:00Z",
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == unique_name
    assert data["is_active"] is True
    assert data['status']=='ENDED'
