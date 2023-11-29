import requests

from . import API_URL

from fastapi import APIRouter, HTTPException, Depends

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

router = APIRouter(prefix="/athlete", tags=["athlete"])


@router.get("/getRaces")
async def get_race_history(
    athlete_id: int, sport: Literal["xc", "tf"] = "xc", level: int = 4
):
    params = dict(athleteId=athlete_id, sport=sport, level=level)
    request = requests.get(API_URL + "/AthleteBio/GetAthleteBioData", params=params)

    result_key = "results" + str.upper(sport)

    results = request.json()[result_key]

    results_output = [
        {
            "anet_resultid": race["IDResult"],
            "anet_meetid": race["MeetID"],
            "result": race["Result"],
            "distance": race["Distance"],
            "place": race["Place"],
            "pb": race["PersonalBest"],
            "sb": race["SeasonBest"],
        }
        for race in results
    ]

    athlete = request.json()["athlete"]
    athlete_output = {
        "anet_athleteid": athlete["IDAthlete"],
        "anet_schoolid": athlete["SchoolID"],
        "first_name": athlete["FirstName"],
        "last_name": athlete["LastName"],
        "gender": athlete["Gender"],
        "age": athlete["age"],
        "races": results_output,
    }

    # TODO: handle eventsTF dict for track results

    return athlete_output


@router.post("/addAthlete", response_model=AthleteRead)
def add_athlete(athlete: AthleteCreate, session: Session = Depends(get_db)):
    athlete_check = get_athlete_by_anet_id(session, anet_id=athlete.anet_id)
    if athlete_check:
        raise HTTPException(status_code=400, detail="Athlete already exists")
    return create_athlete(session, athlete)
