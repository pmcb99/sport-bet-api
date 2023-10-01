
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


def test_create_sport():
    # Test with valid data
    unique_name = "Basketball_" + str(uuid.uuid4())
    response = client.post(
        "/sport",  # make sure this is the correct endpoint
        json={"name": unique_name, "is_active": True},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == unique_name
    assert data["is_active"] == True
    assert "id" in data
    assert "slug" in data
    
    # Test creating a sport with the same name
    response = client.post(
        "/sport",  # corrected to the assumed correct endpoint
        json={"name": unique_name, "is_active": True},
    )
    assert response.status_code == 400, response.text  # corrected to expect a 400 status code
    assert response.json()["detail"] == "Please provide a unique sport name"
    
    # Test with invalid data
    response = client.post(
        "/sport",  # corrected to the assumed correct endpoint
        json={},
    )
    assert response.status_code == 422, response.text  # 422 Unprocessable Entity for validation error
