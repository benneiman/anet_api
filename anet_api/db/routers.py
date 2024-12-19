from sqlmodel import Session

from fastapi import APIRouter, HTTPException, Depends, Query

from anet_api.db import (
    TeamRead,
    TeamCreate,
    AthleteRead,
    AthleteCreate,
    ResultRead,
    ResultCreate,
    Result,
    MeetRead,
    MeetCreate,
    Team,
    Athlete,
    Meet,
    Result,
    Race,
)
from anet_api.constants import (
    DB,
    DB_PREFIX,
    POST_TEAM,
    TEAM,
    POST_ATHLETE,
    ATHLETE,
    POST_RESULT,
    MEET,
    POST_MEET,
)

from anet_api.db.database import get_db
from anet_api.db.utils import (
    create_team,
    create_athlete,
    create_result,
    create_meet,
    convert_to_seconds,
    get_object_by_anet_id,
)


router = APIRouter(prefix=DB_PREFIX, tags=[DB])


@router.post(POST_TEAM, response_model=TeamRead, tags=[TEAM])
async def add_team(team: TeamCreate, session: Session = Depends(get_db)):
    team_check = get_object_by_anet_id(session, anet_id=team.anet_id, obj=Team)
    if team_check:
        raise HTTPException(status_code=400, detail="Team already exists")
    return create_team(session, team)


@router.post(POST_ATHLETE, response_model=AthleteRead, tags=[ATHLETE])
async def add_athlete(athlete: AthleteCreate, session: Session = Depends(get_db)):
    athlete_check = get_object_by_anet_id(session, anet_id=athlete.anet_id, obj=Athlete)
    if athlete_check:
        raise HTTPException(status_code=400, detail="Athlete already exists")
    return create_athlete(session, athlete)


@router.post(POST_RESULT, response_model=ResultRead, tags=[MEET])
async def add_result(result: ResultCreate, session: Session = Depends(get_db)):
    result_check = get_object_by_anet_id(session, anet_id=result.anet_id, obj=Result)
    if result_check:
        raise HTTPException(status_code=400, detail="Result already exists")

    team = get_object_by_anet_id(session, anet_id=result.anet_team_id, obj=Team)
    if not team:
        raise HTTPException(
            status_code=400, detail="This team does not exist in the db"
        )
    athlete = get_object_by_anet_id(
        session, anet_id=result.anet_athlete_id, obj=Athlete
    )
    if not athlete:
        raise HTTPException(
            status_code=400, detail="This athlete does not exist in the db"
        )
    meet = get_object_by_anet_id(session, anet_id=result.anet_meet_id, obj=Meet)
    if not meet:
        raise HTTPException(
            status_code=400, detail="This meet does not exist in the db"
        )
    race = get_object_by_anet_id(session, anet_id=result.anet_race_id, obj=Race)
    if not race:
        raise HTTPException(
            status_code=400, detail="This race does not exist in the db"
        )

    post_result = Result()
    post_result.team_id = team.id
    post_result.athlete_id = athlete.id
    post_result.meet_id = meet.id
    post_result.race_id = race.id
    post_result.result = convert_to_seconds(result.result)
    post_result.anet_id = result.anet_id
    post_result.pb = result.pb
    post_result.sb = result.sb
    post_result.place = result.place

    return create_result(session, post_result)


@router.post(POST_MEET, response_model=MeetRead, tags=[MEET])
async def add_meet(meet: MeetCreate, session: Session = Depends(get_db)):
    meet_check = get_object_by_anet_id(session, anet_id=meet.anet_id, obj=Meet)
    if meet_check:
        raise HTTPException(status_code=400, detail="Meet already exists")
    return create_meet(session, meet)
