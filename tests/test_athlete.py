from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db import Athlete


def test_create_athlete_duplicate(session: Session, client: TestClient):
    data = {
        "anet_id": 1234,
        "first_name": "John",
        "last_name": "Doe",
        "gender": "F",
        "age": None,
    }

    athlete = Athlete(**data)
    session.add(athlete)
    session.commit()

    response = client.post("/athlete/addAthlete", json=data)

    assert response.status_code == 400


def test_create_athlete_invalid(session: Session, client: TestClient):
    data = {
        "anet_id": None,
        "first_name": "John",
        "last_name": "Doe",
        "gender": "F",
        "age": None,
    }

    response = client.post("/athlete/addAthlete", json=data)

    assert response.status_code == 422
