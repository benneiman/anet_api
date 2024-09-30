from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db import Team
from anet_api.constants import ANET_PREFIX, GET_TEAM, DB_PREFIX, POST_TEAM

from tests.data import team_info

get_team_endpoint = ANET_PREFIX + GET_TEAM

post_team_endpoint = DB_PREFIX + POST_TEAM


def test_get_team_info(client: TestClient):
    params = dict(team_id=9352, sport="xc", season=2020)
    response = client.get(get_team_endpoint, params=params)

    assert response.status_code == 200
    assert response.json() == team_info


def test_get_team_info_invalid(client: TestClient):
    params = dict(team_id=493, sport="abc", season=2023)
    response = client.get(get_team_endpoint, params=params)

    assert response.status_code == 422


def test_create_team(client: TestClient):
    response = client.post(
        post_team_endpoint, json={"anet_id": 493, "name": "Garfield"}
    )

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

    response = client.post(post_team_endpoint, json=data)

    assert response.status_code == 400


def test_create_team_invalid(session: Session, client: TestClient):
    data = {"anet_id": 123, "name": None}

    response = client.post(post_team_endpoint, json=data)

    assert response.status_code == 422
