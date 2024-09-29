import requests

from . import API_URL

from datetime import datetime

from sqlmodel import Session

from typing import Literal
from fastapi import APIRouter, HTTPException, Depends, Query

from anet_api.anet import RosterInfo, ScheduleInfo, TeamDetails, TeamInfo, TeamInfoRead
from anet_api.db import (
    TeamRead,
    TeamCreate,
)

from anet_api.db.database import get_db
from anet_api.db.utils import (
    create_team,
    get_team_by_anet_id,
)


router = APIRouter(prefix="/team", tags=["team"])


@router.get("/getInfo", response_model=TeamInfoRead)
async def get_team_info(
    season: int,
    sport: Literal["xc", "tfo", "tfi"] = "xc",
    team_id: int = Query(None, gt=0),
):
    td_sport = "tf" if sport == "tfo" else sport
    team_data = requests.get(
        API_URL + "/TeamNav/Team",
        params=dict(team=team_id, sport=td_sport, season=season),
    )

    team_core = requests.get(
        API_URL + "/TeamHome/GetTeamCore",
        dict(teamId=team_id, sport=sport, season=season),
    )
    anettokens = team_core.json()["jwtTeamHome"]
    headers = {"anettokens": anettokens}
    roster = requests.get(
        API_URL + "/TeamHome/GetAthletes",
        headers=headers,
        params=dict(seasonID=season),
    )

    team_info = team_data.json()["team"]
    team_output = {
        "anet_id": team_id,
        "name": team_info["Name"],
        "city": team_info["City"],
        "state": team_info["State"],
        "mascot": team_info["Mascot"],
    }

    team_details = TeamDetails(**team_output)

    team = TeamInfo(team_data=team_details)
    for athlete in roster.json():
        roster_spot = RosterInfo(
            anet_id=athlete["ID"],
            first_name=athlete["Name"].split(" ", 1)[0],
            last_name=athlete["Name"].rsplit(" ", 1)[1],
            gender=athlete["Gender"],
        )
        team.roster.append(roster_spot)

    schedule = requests.get(
        API_URL + "/TeamHomeCal/GetCalendar",
        headers=headers,
        params=dict(seasonID=season),
    )

    for meet in schedule.json():
        meet_info = ScheduleInfo(
            anet_id=meet["MeetID"],
            meet=meet["Name"],
            venue=meet["Location"]["Name"],
            address=meet["StreetAddress"],
            city=meet["City"],
            state=meet["State"],
            zipcode=None if meet["PostalCode"] == "" else meet["PostalCode"],
            date=datetime.strptime(meet["StartDate"], "%Y-%m-%dT%H:%M:%S").date(),
        )
        team.schedule.append(meet_info)

    return team


@router.post("/addTeam", response_model=TeamRead)
async def add_team(team: TeamCreate, session: Session = Depends(get_db)):
    team_check = get_team_by_anet_id(session, anet_id=team.anet_id)
    if team_check:
        raise HTTPException(status_code=400, detail="Team already exists")
    return create_team(session, team)
