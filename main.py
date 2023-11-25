import requests

from fastapi import FastAPI, HTTPException, Depends

from sqlmodel import Session
from db import Team

from db.database import SessionLocal
from db.utils import create_team

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
    team_info = team_data.json()["team"]

    schedule = requests.get(
        "https://www.athletic.net/api/v1/TeamHomeCal/GetCalendar",
        headers=headers,
        params=dict(seasonID=season),
    )
    schedule_output = [
        {
            "meet_name": meet["Name"],
            "anet_meet_id": meet["MeetID"],
            "street_address": meet["StreetAddress"],
            "city": meet["City"],
            "state": meet["State"],
            "zipcode": meet["PostalCode"],
            "location": meet["Location"],
            "date": meet["Date"],
        }
        for meet in schedule.json()
    ]
    return {
        "name": team_info["Name"],
        "city": team_info["City"],
        "state": team_info["State"],
        "mascot": team_info["Mascot"],
        "roster": roster.json(),
        "schedule": schedule_output,
    }


@app.post("/team/addTeam", response_model=Team)
async def add_team(team: Team, session: Session = Depends(get_db)):
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
            "location": meet_payload["meet"]["Location"]["Name"],
            "street_address": meet_payload["meet"]["Location"]["Address"],
            "city": meet_payload["meet"]["Location"]["City"],
            "state": meet_payload["meet"]["Location"]["State"],
            "zipcode": meet_payload["meet"]["Location"]["PostalCode"],
        },
        "races": [
            {
                "race_id": race["IDMeetDiv"],
                "race": race["DivName"],
                "division": race["Division"],
                "place_depth": race["PlaceDepth"],
                "score_depth": race["ScoreDepth"],
                "start_time": race["RaceTime"],
                "results": [],
                "team_scores": [],
            }
            for race in meet_payload["xcDivisions"]
        ],
    }

    results = requests.get(
        "https://www.athletic.net/api/v1/Meet/GetAllResultsData",
        headers=dict(
            referer="https://www.athletic.net/CrossCountry/meet/225886/results/all",
            anettokens=meet_payload["jwtMeet"],
        ),
    )

    for finisher in results.json()["results"]:
        finisher_details = {
            "athlete_id": finisher["AthleteID"],
            "name": finisher["FirstName"] + " " + finisher["LastName"],
            "team_id": finisher["TeamID"],
            "team": finisher["SchoolName"],
            "grade": finisher["AgeGrade"],
            "result": finisher["Result"],
            "place": finisher["Place"],
        }
        race_id = finisher["RaceDivisionID"]
        for race in meet_data["races"]:
            if race_id == race["race_id"]:
                race["results"].append(finisher_details)

    for team_score in results.json()["teamScores"]:
        score_copy = team_score.copy()
        for race in meet_data["races"]:
            if team_score["DivisionID"] == race["race_id"]:
                score_copy.pop("DivisionID")
                score_copy.pop("rawName")
                race["team_scores"].append(score_copy)

    return meet_data


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
