from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db import Race
from anet_api.constants import DB_PREFIX, POST_RACE


post_race_endpoint = DB_PREFIX + POST_RACE


def test_create_team(client: TestClient):
    data = {
        "anet_id": 123,
        "gender": "M",
        "race_name": "fake race",
        "division": "idk",
        "place_depth": 7,
        "score_depth": 5,
        "start_time": "2024-12-19T18:57:48.506000",
        "distance": 100,
    }
    response = client.post(post_race_endpoint, json=data)

    data = response.json()

    assert response.status_code == 200
    assert data["anet_id"] == 123
    assert data["gender"] == "M"
    assert data["race_name"] == "fake race"
    assert data["division"] == "idk"
    assert data["place_depth"] == 7
    assert data["score_depth"] == 5
    assert data["distance"] == 100
    assert data["id"] is not None


def test_create_team_duplicate(session: Session, client: TestClient):
    data = {
        "anet_id": 123,
        "gender": "M",
        "race_name": "rake race",
        "division": "idk",
        "place_depth": 7,
        "score_depth": 5,
        "start_time": "2024-12-19T18:57:48.506000",
        "distance": 100,
    }
    team = Race(**data)

    session.add(team)
    session.commit()

    response = client.post(post_race_endpoint, json=data)

    assert response.status_code == 400


def test_create_team_invalid(session: Session, client: TestClient):
    data = {
        "anet_id": 100,
        "gender": "M",
        "race_name": "rake race",
        "division": 1234,  # wrong datatype
        "place_depth": 7,
        "score_depth": 5,
        "start_time": "2024-12-19T18:57:48.506000",
        "distance": 100,
    }

    response = client.post(post_race_endpoint, json=data)

    assert response.status_code == 422
