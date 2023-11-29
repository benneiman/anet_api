from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db import Team

from tests.data import team_info


def test_get_team_info(client: TestClient):
    params = dict(team_id=1, sport="xc", season=2023)
    response = client.get("/team/getInfo", params=params)

    assert response.status_code == 200
    assert response.json() == team_info


def test_get_team_info_invalid(client: TestClient):
    params = dict(team_id=493, sport="abc", season=2023)
    response = client.get("/team/getInfo", params=params)

    assert response.status_code == 422


def test_create_team(client: TestClient):
    response = client.post("/team/addTeam", json={"anet_id": 493, "name": "Garfield"})

    data = response.json()

    assert response.status_code == 200
    assert data["anet_id"] == 493
    assert data["name"] == "Garfield"
    assert data["id"] is not None


def test_create_team_duplicate(session: Session, client: TestClient):
    data = {"anet_id": 123, "name": "New Team"}
    team = Team(**data)

    session.add(team)
    session.commit()

    response = client.post("/team/addTeam", json=data)

    assert response.status_code == 400


def test_create_team_invalid(session: Session, client: TestClient):
    data = {"anet_id": 123, "name": None}

    response = client.post("/team/addTeam", json=data)

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
