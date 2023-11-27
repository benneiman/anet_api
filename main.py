import requests

from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends

from sqlmodel import Session
from db import (
    TeamRead,
    TeamCreate,
    AthleteRead,
    AthleteCreate,
    Result,
    ResultRead,
    ResultCreate,
    MeetRead,
    MeetCreate,
)

from db.database import SessionLocal
from db.utils import (
    create_team,
    create_athlete,
    create_meet,
    create_result,
    get_team_by_anet_id,
    get_athlete_by_anet_id,
    get_meet_by_anet_id,
    get_result_by_anet_id,
    convert_to_seconds,
)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/team/getInfo")
async def team_info(team_id: int, sport: str, season: int):
    if sport not in ("xc", "tfo", "tfi"):
        raise HTTPException(
            status_code=400, detail=f"Bad request: {sport} not a valid option"
        )
    td_sport = "tf" if sport == "tfo" else sport
    team_data = requests.get(
        "https://www.athletic.net/api/v1/TeamNav/Team",
        params=dict(team=team_id, sport=td_sport, season=season),
    )

    team_core = requests.get(
        "https://www.athletic.net/api/v1/TeamHome/GetTeamCore",
        dict(teamId=team_id, sport=sport, season=season),
    )
    anettokens = team_core.json()["jwtTeamHome"]
    referer_url = f"https://www.athletic.net/team/{team_id}/cross-country/{season}"
    headers = {"referer": referer_url, "anettokens": anettokens}
    roster = requests.get(
        "https://www.athletic.net/api/v1/TeamHome/GetAthletes",
        headers=headers,
        params=dict(seasonID=season),
    )

    roster_output = [
        {
            "anet_id": athlete["ID"],
            "first_name": athlete["Name"].split(" ", 1)[0],
            "last_name": athlete["Name"].rsplit(" ", 1)[1],
            "gender": athlete["Gender"],
        }
        for athlete in roster.json()
    ]
    team_info = team_data.json()["team"]

    schedule = requests.get(
        "https://www.athletic.net/api/v1/TeamHomeCal/GetCalendar",
        headers=headers,
        params=dict(seasonID=season),
    )
    schedule_output = [
        {
            "name": meet["Name"],
            "venue": meet["Location"]["Name"],
            "anet_id": meet["MeetID"],
            "address": meet["StreetAddress"],
            "city": meet["City"],
            "state": meet["State"],
            "zipcode": None if meet["PostalCode"] == "" else meet["PostalCode"],
            # "location": meet["Location"],
            "date": datetime.strptime(meet["StartDate"], "%Y-%m-%dT%H:%M:%S").date(),
        }
        for meet in schedule.json()
    ]
    return {
        "team_data": {
            "name": team_info["Name"],
            "city": team_info["City"],
            "state": team_info["State"],
            "mascot": team_info["Mascot"],
        },
        "roster": roster_output,
        "schedule": schedule_output,
    }


@app.post("/team/addTeam", response_model=TeamRead)
async def add_team(team: TeamCreate, session: Session = Depends(get_db)):
    team_check = get_team_by_anet_id(session, anet_id=team.anet_id)
    if team_check:
        raise HTTPException(status_code=400, detail="Team already exists")
    return create_team(session, team)


@app.get("/meet/getResults")
async def get_meet_results(meet_id: int, sport: str):
    if sport not in ("xc", "tf"):
        raise HTTPException(
            status_code=400, detail=f"Bad request: {sport} not a valid option"
        )
    params = dict(meetId=meet_id, sport=sport)
    meet = requests.get(
        "https://www.athletic.net/api/v1/Meet/GetMeetData", params=params
    )

    meet_payload = meet.json()

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
        "https://www.athletic.net/api/v1/Meet/GetAllResultsData",
        headers=dict(
            referer="https://www.athletic.net/CrossCountry/meet/225886/results/all",
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


@app.post("/meet/addResult", response_model=ResultRead)
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


@app.post("/meet/addMeet", response_model=MeetRead)
async def add_meet(meet: MeetCreate, session: Session = Depends(get_db)):
    meet_check = get_meet_by_anet_id(session, anet_id=meet.anet_id)
    if meet_check:
        raise HTTPException(status_code=400, detail="Meet already exists")
    return create_meet(session, meet)


@app.get("/athlete/getRaces")
async def get_race_history(athlete_id: int, sport: str, level: int = 4):
    params = dict(athleteId=athlete_id, sport=sport, level=level)
    request = requests.get(
        "https://www.athletic.net/api/v1/AthleteBio/GetAthleteBioData", params=params
    )

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
        "gender": athlete["Gender"],
        "age": athlete["age"],
        "races": results_output,
    }

    # TODO: handle eventsTF dict for track results

    return athlete_output


@app.post("/athlete/addAthlete", response_model=AthleteRead)
def add_athlete(athlete: AthleteCreate, session: Session = Depends(get_db)):
    athlete_check = get_athlete_by_anet_id(session, anet_id=athlete.anet_id)
    if athlete_check:
        raise HTTPException(status_code=400, detail="Athlete already exists")
    return create_athlete(session, athlete)


@app.get("/search/getResults")
async def get_search_results(query: str):
    """Search API
    Wrapper for
    """
    params = dict(q=query)
    request = requests.get(
        "https://www.athletic.net/api/v1/AutoComplete/search", params=params
    )
    return request.json()
