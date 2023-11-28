from fastapi.testclient import TestClient


def test_anet_get_team(client: TestClient):
    params = dict(team_id=493, sport="xc", season=2023)
    response = client.get("/team/getInfo", params=params)

    assert response.status_code == 200


def test_anet_get_team_invalid(client: TestClient):
    params = dict(team_id=493, sport="abc", season=2023)
    response = client.get("/team/getInfo", params=params)

    assert response.status_code == 422


def test_anet_get_team_missing(client: TestClient):
    params = dict(team_id=0, sport="xc", season=2023)
    response = client.get("/team/getInfo", params=params)

    assert response.status_code == 404
