import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from anet_api.db.utils import get_object_by_anet_id, convert_to_seconds

from anet_api.db import Team, AthleteCreate
from anet_api.constants import DB_PREFIX, POST_TEAM

post_team_endpoint = DB_PREFIX + POST_TEAM


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
    assert (
        str(e_info.value)
        == "Only Athlete, Team, Result, Meet, or Race models can be passed"
    )
