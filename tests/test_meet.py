from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db import Team, Athlete, Meet

from tests.data import meet_results, schedule


############################
#####   CREATE Tests  ######
############################
def test_create_meet(client: TestClient):
    response = client.post(
        "/meet/addMeet",
        json={
            "anet_id": 4321,
            "meet": "League Meet #1",
            "venue": "Echo Park",
            "address": "123 America St",
            "city": "Seattle",
            "state": "OR",
            "zipcode": 10001,
            "date": "2023-11-27",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["anet_id"] == 4321
    assert data["meet"] == "League Meet #1"
    assert data["venue"] == "Echo Park"
    assert data["address"] == "123 America St"
    assert data["city"] == "Seattle"
    assert data["state"] == "OR"
    assert data["zipcode"] == 10001
    assert data["id"] is not None


def test_create_meet_duplicate(session: Session, client: TestClient):
    data = {
        "anet_id": 4321,
        "meet": "League Meet #1",
        "venue": "Echo Park",
        "address": "123 America St",
        "city": "Seattle",
        "state": "OR",
        "zipcode": 10001,
        "date": "2023-11-27",
    }

    meet = Meet(**data)
    session.add(meet)
    session.commit()

    response = client.post("/meet/addMeet", json=data)

    assert response.status_code == 400


def test_create_result(session: Session, client: TestClient):
    team = Team(anet_id=111, name="New Team")
    athlete = Athlete(anet_id=222, first_name="John", last_name="Doe", gender="F")
    meet = Meet(anet_id=333, meet="New Meet", venue="Place", date="2023-01-01")

    session.add(team)
    session.add(athlete)
    session.add(meet)
    session.commit()
    response = client.post(
        "/meet/addResult",
        json={
            "anet_id": 5678,
            "distance": None,
            "place": 1,
            "pb": True,
            "sb": True,
            "anet_athlete_id": 222,
            "anet_team_id": 111,
            "anet_meet_id": 333,
            "result": "20:00",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["anet_id"] == 5678
    assert data["distance"] == None
    assert data["place"] == 1
    assert data["pb"] == True
    assert data["sb"] == True
    assert data["athlete_id"] == 1
    assert data["team_id"] == 1
    assert data["meet_id"] == 1
    assert data["result"] == 1200.0
    assert data["id"] is not None


#########################
#####    GET Tests ######
#########################
def test_get_meet_results(client: TestClient):
    params = dict(meet_id=161636, sport="xc")
    response = client.get("/meet/getResults", params=params)

    assert response.status_code == 200
    assert response.json()["meet_details"] == meet_results["meet_details"]
    assert response.json()["teams"] == meet_results["teams"]
    assert response.json()["races"] == meet_results["races"]


def test_get_meet_results_invalid(client: TestClient):
    params = dict(meet_id=221788, sport="abc")
    response = client.get("/meet/getResults", params=params)

    assert response.status_code == 422


def test_get_meet_results_404(client: TestClient):
    params = dict(meet_id=0, sport="xc")
    response = client.get("/meet/getResults", params=params)

    assert response.status_code == 404


def test_get_schedule(client: TestClient):
    params = dict(
        start_date="2019-09-05",
        end_date="2019-09-08",
        level=4,
        sport="xc",
        state="WA",
        country="us",
    )
    response = client.get("/meet/getSchedule", params=params)

    assert response.status_code == 200
    assert response.json() == schedule


def test_get_schedule_invalid(client: TestClient):
    params = dict(
        start="invalid input",
        end="2019-09-08",
        levelMask=4,
        sportMask=2,
        state="WA",
        country="us",
    )
    response = client.get("/meet/getSchedule", params=params)

    assert response.status_code == 422
