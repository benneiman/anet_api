import requests

from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/team/")
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


@app.get("/meet/")
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
    return meet_data
