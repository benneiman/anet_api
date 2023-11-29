from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db import Athlete

from tests.data import race_history


def test_get_race_history(client: TestClient):
    params = dict(athlete_id=5, sport="xc", level=4)
    response = client.get("/athlete/getRaces", params=params)

    assert response.status_code == 200
    assert response.json() == race_history


def test_get_race_history_invalid(client: TestClient):
    params = dict(athlete_id=21133877, sport="abc", level=4)
    response = client.get("/athlete/getRaces", params=params)

    assert response.status_code == 422


def test_create_athlete(client: TestClient):
    response = client.post(
        "/athlete/addAthlete",
        json={
            "anet_id": 1234,
            "first_name": "John",
            "last_name": "Doe",
            "gender": "F",
            "age": None,
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["anet_id"] == 1234
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["gender"] == "F"
    assert data["age"] is None
    assert data["id"] is not None


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
