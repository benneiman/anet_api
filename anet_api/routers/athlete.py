import requests

from . import API_URL

from fastapi import APIRouter, HTTPException, Depends, Query

from typing import Literal

from sqlmodel import Session

from anet_api.db import (
    AthleteRead,
    AthleteCreate,
)

from anet_api.db.database import SessionLocal, get_db
from anet_api.db.utils import (
    create_athlete,
    get_athlete_by_anet_id,
)

from anet_api.anet import AthleteInfoRead, AthleteInfo, AthleteDetails, ResultInfo

router = APIRouter(prefix="/athlete", tags=["athlete"])


@router.get("/getRaces", response_model=AthleteInfoRead)
async def get_race_history(
    athlete_id: int = Query(None, gt=0),
    sport: Literal["xc", "tf"] = "xc",
    level: int = 4,
):
    params = dict(athleteId=athlete_id, sport=sport, level=level)
    response = requests.get(API_URL + "/AthleteBio/GetAthleteBioData", params=params)

    result_key = "results" + str.upper(sport)

    results = response.json()[result_key]

    athlete = response.json()["athlete"]
    athlete_output = {
        "anet_id": athlete["IDAthlete"],
        "anet_team_id": athlete["SchoolID"],
        "first_name": athlete["FirstName"],
        "last_name": athlete["LastName"],
        "gender": athlete["Gender"],
        "age": athlete["age"],
    }
    athlete_details = AthleteDetails(**athlete_output)
    athlete_info = AthleteInfo(athlete_data=athlete_details)

    for result in results:
        result_info = ResultInfo(
            anet_id=result["IDResult"],
            anet_meet_id=result["MeetID"],
            anet_athlete_id=athlete_id,
            result=result["Result"],
            distance=result["Distance"],
            place=result["Place"],
            pb=result["PersonalBest"],
            sb=result["SeasonBest"],
        )
        athlete_info.races.append(result_info)

    return athlete_info


@router.post("/addAthlete", response_model=AthleteRead)
def add_athlete(athlete: AthleteCreate, session: Session = Depends(get_db)):
    athlete_check = get_athlete_by_anet_id(session, anet_id=athlete.anet_id)
    if athlete_check:
        raise HTTPException(status_code=400, detail="Athlete already exists")
    return create_athlete(session, athlete)
