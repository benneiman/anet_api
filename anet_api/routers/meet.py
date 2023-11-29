import requests

from . import API_URL

from fastapi import APIRouter, HTTPException, Depends

from typing import Optional, Literal

from sqlmodel import Session

from anet_api.db import (
    Result,
    ResultRead,
    ResultCreate,
    MeetRead,
    MeetCreate,
)

from anet_api.db.database import get_db
from anet_api.db.utils import (
    create_meet,
    create_result,
    get_team_by_anet_id,
    get_athlete_by_anet_id,
    get_meet_by_anet_id,
    get_result_by_anet_id,
    convert_to_seconds,
)

router = APIRouter(prefix="/meet", tags=["meet"])


@router.get("/getSchedule", tags=["meet"])
async def get_meet_schedule(
    start_date: str,
    end_date: str,
    state: str,
    country: str = "us",
    level: Optional[int] = 4,
    sport: Literal["xc", "tf", "all"] = "all",
    location: Optional[str] = None,
):
    sport_mask = ["all", "tf", "xc"]
    payload = dict(
        start=start_date,
        end=end_date,
        levelMask=level,
        sportMask=sport_mask.index(sport),
        state=state,
        country=country,
        location=location,
    )

    events = requests.post(API_URL + "/Event/Events", json=payload)
    return events.json()


@router.get("/getResults")
async def get_meet_results(meet_id: int, sport: Literal["xc", "tf"]):
    params = dict(meetId=meet_id, sport=sport)
    meet = requests.get(API_URL + "/Meet/GetMeetData", params=params)

    meet_payload = meet.json()

    if not meet_payload:
        raise HTTPException(status_code=404, detail="Meet does not exist")

    meet_data = {
        "meet": {
            "anet_meet_id": meet_id,
            "location": meet_payload["meet"]["Location"]["Name"],
            "address": meet_payload["meet"]["Location"]["Address"],
            "city": meet_payload["meet"]["Location"]["City"],
            "state": meet_payload["meet"]["Location"]["State"],
            "zipcode": meet_payload["meet"]["Location"]["PostalCode"],
        },
        "races": [],
    }

    results = requests.get(
        API_URL + "/Meet/GetAllResultsData",
        headers=dict(
            anettokens=meet_payload["jwtMeet"],
        ),
    )

    for race in results.json()["flatEvents"]:
        race_details = {
            "race_id": race["IDMeetDiv"],
            "gender": race["Gender"],
            "race_name": race["DivName"],
            "division": race["Division"],
            "place_depth": race["PlaceDepth"],
            "score_depth": race["ScoreDepth"],
            "start_time": race["RaceTime"],
            "results": [],
            "team_scores": [],
        }
        for finisher in race["results"]:
            finisher_details = {
                "anet_id": finisher["IDResult"],
                "anet_meet_id": meet_id,
                "anet_athlete_id": finisher["AthleteID"],
                "first_name": finisher["FirstName"],
                "last_name": finisher["LastName"],
                "anet_team_id": finisher["TeamID"],
                "team": finisher["SchoolName"],
                "grade": finisher["AgeGrade"],
                "result": finisher["Result"],
                "place": finisher["Place"],
                "pb": finisher["pr"],
                "sb": finisher["sr"],
            }
            race_details["results"].append(finisher_details)
        meet_data["races"].append(race_details)

        for team_score in results.json()["teamScores"]:
            score_copy = team_score.copy()
            for race in meet_data["races"]:
                if team_score["DivisionID"] == race["race_id"]:
                    score_copy.pop("DivisionID")
                    score_copy.pop("rawName")
                    score_copy.pop("Gender")
                    race["team_scores"].append(score_copy)

    return meet_data


@router.post("/meet/addResult", response_model=ResultRead)
async def add_result(result: ResultCreate, session: Session = Depends(get_db)):
    result_check = get_result_by_anet_id(session, anet_id=result.anet_id)
    if result_check:
        raise HTTPException(status_code=400, detail="Result already exists")

    team = get_team_by_anet_id(session, result.anet_team_id)
    if not team:
        raise HTTPException(
            status_code=400, detail="This team does not exist in the db"
        )
    athlete = get_athlete_by_anet_id(session, result.anet_athlete_id)
    if not athlete:
        raise HTTPException(
            status_code=400, detail="This athlete does not exist in the db"
        )
    meet = get_meet_by_anet_id(session, result.anet_meet_id)
    if not meet:
        raise HTTPException(
            status_code=400, detail="This meet does not exist in the db"
        )

    post_result = Result()
    post_result.team_id = team.id
    post_result.athlete_id = athlete.id
    post_result.meet_id = meet.id
    post_result.result = convert_to_seconds(result.result)
    post_result.anet_id = result.anet_id
    post_result.pb = result.pb
    post_result.sb = result.sb
    post_result.place = result.place

    return create_result(session, post_result)


@router.post("/addMeet", response_model=MeetRead)
async def add_meet(meet: MeetCreate, session: Session = Depends(get_db)):
    meet_check = get_meet_by_anet_id(session, anet_id=meet.anet_id)
    if meet_check:
        raise HTTPException(status_code=400, detail="Meet already exists")
    return create_meet(session, meet)
