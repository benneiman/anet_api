from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db import Athlete
from anet_api.constants import ANET_PREFIX, DB_PREFIX, POST_ATHLETE, GET_RACES

from tests.data import race_history

get_races_endpoint = ANET_PREFIX + GET_RACES
post_athlete_endpoint = DB_PREFIX + POST_ATHLETE


def test_get_race_history(client: TestClient):
    params = dict(athlete_id=5, sport="xc", level=4)
    response = client.get(get_races_endpoint, params=params)

    assert response.status_code == 200
    assert response.json()["athlete_data"] == race_history["athlete_data"]
    assert response.json()["races"] == race_history["races"]


def test_get_race_history_invalid(client: TestClient):
    params = dict(athlete_id=21133877, sport="abc", level=4)
    response = client.get(get_races_endpoint, params=params)

    assert response.status_code == 422


def test_create_athlete(client: TestClient):
    response = client.post(
        post_athlete_endpoint,
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

    response = client.post(post_athlete_endpoint, json=data)

    assert response.status_code == 400


def test_create_athlete_invalid(session: Session, client: TestClient):
    data = {
        "anet_id": None,
        "first_name": "John",
        "last_name": "Doe",
        "gender": "F",
        "age": None,
    }

    response = client.post(post_athlete_endpoint, json=data)

    assert response.status_code == 422
