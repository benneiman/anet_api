from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db import Team


def test_get_team_info(client: TestClient):
    params = dict(team_id=1, sport="xc", season=2023)
    response = client.get("/team/getInfo", params=params)

    assert response.status_code == 200
    assert response.json() == {
        "team_data": {
            "name": "New Hope Christian",
            "city": "Grants Pass",
            "state": "OR",
            "mascot": "Warriors",
        },
        "roster": [
            {
                "anet_id": 23678399,
                "first_name": "Alijah",
                "last_name": "Williams",
                "gender": "M",
                "age": None,
            },
            {
                "anet_id": 23843443,
                "first_name": "Colton",
                "last_name": "Wright",
                "gender": "M",
                "age": None,
            },
            {
                "anet_id": 23638350,
                "first_name": "Peighton",
                "last_name": "Wharregard",
                "gender": "M",
                "age": None,
            },
            {
                "anet_id": 23638333,
                "first_name": "Thomas",
                "last_name": "Sheets",
                "gender": "M",
                "age": None,
            },
        ],
        "schedule": [
            {
                "anet_id": 224755,
                "meet": "Myrtle Point Harvest Festival",
                "venue": "Myrtle Point High School",
                "address": "717 4th Street",
                "city": "Myrtle Point",
                "state": "OR",
                "zipcode": 97458,
                "date": "2023-09-09",
            },
            {
                "anet_id": 223847,
                "meet": "Rogue XC Invitational ",
                "venue": "Colver Fields",
                "address": "6100 Colver Rd",
                "city": "Talent",
                "state": "OR",
                "zipcode": 97540,
                "date": "2023-09-16",
            },
            {
                "anet_id": 222689,
                "meet": "Glide Invitational - This Run's For Maynard",
                "venue": "Glide High School",
                "address": None,
                "city": "Glide",
                "state": "OR",
                "zipcode": 97443,
                "date": "2023-09-21",
            },
            {
                "anet_id": 228583,
                "meet": "Project Youth + 5K & 1-Mile",
                "venue": "Project Youth + 5K",
                "address": "2160 NW Vine St",
                "city": "Grants Pass",
                "state": "OR",
                "zipcode": 97526,
                "date": "2023-09-30",
            },
            {
                "anet_id": 222839,
                "meet": "Stan Goodell The Legend Invite",
                "venue": "Hidden Valley High School",
                "address": "651 Murphy Creek Rd.",
                "city": "Grants Pass",
                "state": "OR",
                "zipcode": 97527,
                "date": "2023-10-07",
            },
            {
                "anet_id": 223158,
                "meet": "Days Creek Relays",
                "venue": "Days Creek Charter School",
                "address": "11381 Tiller-Trail Highway",
                "city": "Days Creek",
                "state": "OR",
                "zipcode": 97429,
                "date": "2023-10-10",
            },
            {
                "anet_id": 222083,
                "meet": "Umpqua Invite",
                "venue": "Stewart Park",
                "address": "",
                "city": "Roseburg",
                "state": "OR",
                "zipcode": 97471,
                "date": "2023-10-18",
            },
            {
                "anet_id": 222134,
                "meet": "3A/2A/1A-SD4 District 4 Championships",
                "venue": "Valley of the Rogue State Park",
                "address": None,
                "city": "Gold Hill",
                "state": "OR",
                "zipcode": 97525,
                "date": "2023-10-26",
            },
        ],
    }


def test_get_team_info_invalid(client: TestClient):
    params = dict(team_id=493, sport="abc", season=2023)
    response = client.get("/team/getInfo", params=params)

    assert response.status_code == 422


def test_get_team_info_missing(client: TestClient):
    params = dict(team_id=0, sport="xc", season=2023)
    response = client.get("/team/getInfo", params=params)

    assert response.status_code == 404


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
