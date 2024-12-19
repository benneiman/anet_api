import requests

from ..constants import (
    API_URL,
    TEAM,
    ATHLETE,
    MEET,
    SEARCH,
    ANET_PREFIX,
    GET_SCHEDULE,
    GET_MEET,
    GET_RACES,
    GET_RESULTS,
    GET_SEARCH,
    GET_TEAM,
)

from datetime import datetime

from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from anet_api.anet import (
    MeetResultsInfoRead,
    MeetResultsInfo,
    MeetDetails,
    TeamScoreInfo,
    RaceDetails,
    RaceInfo,
    ResultInfo,
    RosterInfo,
    ScheduleInfo,
    TeamDetails,
    TeamInfo,
    TeamInfoRead,
    AthleteInfo,
    AthleteDetails,
    AthleteInfoRead,
)

router = APIRouter(prefix=ANET_PREFIX, tags=["anet"])


@router.get(GET_TEAM, response_model=TeamInfoRead, tags=[TEAM])
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
        "season": season,
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
            address=meet["Location"]["Address"],
            city=meet["Location"]["City"],
            state=meet["Location"]["State"],
            zipcode=(
                None
                if meet["Location"]["PostalCode"] == ""
                else meet["Location"]["PostalCode"]
            ),
            date=datetime.strptime(meet["StartDate"], "%Y-%m-%dT%H:%M:%S").date(),
        )
        team.schedule.append(meet_info)

    return team


@router.get(GET_SCHEDULE, tags=[MEET])
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


@router.get(GET_RESULTS, response_model=MeetResultsInfoRead, tags=[MEET])
async def get_meet_results(meet_id: int, sport: Literal["xc", "tf"]):
    params = dict(meetId=meet_id, sport=sport)
    response = requests.get(API_URL + "/Meet/GetMeetData", params=params)

    meet = response.json()

    if not meet:
        raise HTTPException(status_code=404, detail="Meet does not exist")

    meet_output = {
        "anet_meet_id": meet_id,
        "location": meet["meet"]["Location"]["Name"],
        "address": meet["meet"]["Location"]["Address"],
        "city": meet["meet"]["Location"]["City"],
        "state": meet["meet"]["Location"]["State"],
        "zipcode": (
            None
            if meet["meet"]["Location"]["PostalCode"] == ""
            else meet["meet"]["Location"]["PostalCode"]
        ),
    }
    meet_details = MeetDetails(**meet_output)

    teams = requests.get(
        API_URL + "/Meet/GetTeams", headers=dict(anettokens=meet["jwtMeet"])
    )

    team_list = list()
    for team in teams.json():
        team_detail = TeamDetails(name=team["SchoolName"], anet_id=team["IDSchool"])
        team_list.append(team_detail)

    meet_results_info = MeetResultsInfo(meet_details=meet_details, teams=team_list)

    results = requests.get(
        API_URL + "/Meet/GetAllResultsData",
        headers=dict(
            anettokens=meet["jwtMeet"],
        ),
    )
    race_team_scores = list()
    for team_score in results.json()["teamScores"]:
        team_score_info = TeamScoreInfo(
            anet_team_id=team_score["SchoolID"],
            team=team_score["Name"],
            points=team_score["Points"],
            place=team_score["Place"],
        )
        race_team_scores.append((team_score["DivisionID"], team_score_info))

    for race in results.json()["flatEvents"]:
        race_details = RaceDetails(
            anet_race_id=race["IDMeetDiv"],
            gender=race["Gender"],
            race_name=race["DivName"],
            division=race["Division"],
            place_depth=race["PlaceDepth"],
            score_depth=race["ScoreDepth"],
            start_time=race["RaceTime"],
        )
        race_info = RaceInfo(race_details=race_details)
        for finisher in race["results"]:
            result_info = ResultInfo(
                anet_id=finisher["IDResult"],
                anet_meet_id=meet_id,
                anet_athlete_id=finisher["AthleteID"],
                anet_team_id=finisher["TeamID"],
                first_name=finisher["FirstName"],
                last_name=finisher["LastName"],
                team=finisher["SchoolName"],
                grade=finisher["AgeGrade"],
                result=finisher["Result"],
                place=finisher["Place"],
                pb=finisher["pr"],
                sb=finisher["sr"],
            )
            race_info.results.append(result_info)

        for race_id, team_score in race_team_scores:
            if race_id == race_details.anet_race_id:
                race_info.team_scores.append(team_score)

        meet_results_info.races.append(race_info)

    return meet_results_info


@router.get(GET_RACES, response_model=AthleteInfoRead, tags=[ATHLETE])
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


@router.get(GET_SEARCH, tags=[SEARCH])
async def get_search_results(query: str):
    """Search API
    Wrapper for
    """
    params = dict(q=query)
    request = requests.get(API_URL + "/AutoComplete/search", params=params)
    return request.json()
