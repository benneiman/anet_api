import pytest

from pydantic import ValidationError
from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db.utils import (
    create_item,
    get_object_by_anet_id,
    get_course_by_venue,
    convert_to_seconds,
)

from anet_api.db import Team, TeamCreate, Athlete, AthleteCreate, Course
from anet_api.constants import DB_PREFIX, POST_TEAM, POST_COURSE

post_team_endpoint = DB_PREFIX + POST_TEAM
post_course_endpoint = DB_PREFIX + POST_COURSE


def test_convert_to_seconds():
    t = convert_to_seconds(race_time="20:21")
    assert t == 1221


def test_get_object_by_anet_id(session: Session, client: TestClient):
    response = client.post(
        post_team_endpoint, json={"anet_id": 493, "name": "Garfield"}
    )

    res = get_object_by_anet_id(session, 493, Team)
    assert isinstance(res, Team)


def test_get_object_by_anet_id_invalid(session: Session, client: TestClient):
    response = client.post(
        post_team_endpoint, json={"anet_id": 493, "name": "Garfield"}
    )
    with pytest.raises(TypeError) as e_info:
        get_object_by_anet_id(session, 493, AthleteCreate)


def test_create_item(session: Session, client: TestClient):
    team = TeamCreate(anet_id=1, name="Test Team")
    res = create_item(session, team, Team)
    assert isinstance(res, Team)


def test_create_item_invalid(session: Session, client: TestClient):
    team = TeamCreate(anet_id=1, name="Test Team")
    with pytest.raises(ValidationError) as e_info:
        create_item(session, team, Athlete)


def test_get_course_by_venue(session: Session, client: TestClient):
    response = client.post(
        post_course_endpoint, json={"venue": "fake park", "course_factor": 100}
    )

    res = get_course_by_venue(session, "fake park")
    assert isinstance(res, Course)
