from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import date, datetime


class MeetDetails(BaseModel):
    anet_meet_id: int
    meet: str
    venue: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipcode: Optional[str]


class ScheduleInfo(BaseModel):
    anet_id: int
    meet: str
    venue: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipcode: Optional[str]
    date: Optional[date]


class RosterInfo(BaseModel):
    anet_id: int
    first_name: str
    last_name: str
    gender: Literal["M", "F"]
    age: Optional[int]


class TeamDetails(BaseModel):
    anet_id: int
    name: Optional[str]
    city: Optional[str]
    state: Optional[str]
    mascot: Optional[str]
    season: Optional[int]


class TeamInfo(BaseModel):
    team_data: TeamDetails
    roster: List[RosterInfo] = list()
    schedule: List[ScheduleInfo] = list()


class TeamInfoRead(TeamInfo):
    pass


class ResultInfo(BaseModel):
    anet_id: int
    anet_meet_id: Optional[int]
    anet_athlete_id: Optional[int]
    result: str
    place: Optional[int]
    pb: Optional[bool]
    sb: Optional[bool]
    distance: Optional[int]


class ResultInfoExtended(ResultInfo):
    anet_team_id: Optional[int]
    anet_race_id: Optional[int]
    first_name: Optional[str]
    last_name: Optional[str]
    team: Optional[str]
    grade: Optional[str]
    venue: str | None


class AthleteDetails(BaseModel):
    anet_id: int
    anet_team_id: Optional[int]
    first_name: str
    last_name: str
    gender: Optional[Literal["M", "F"]]
    age: Optional[int]


class AthleteInfo(BaseModel):
    athlete_data: AthleteDetails
    races: List[ResultInfo] = list()


class AthleteInfoRead(AthleteInfo):
    pass


class TeamScoreInfo(BaseModel):
    place: Optional[int]
    anet_team_id: Optional[int]
    team: Optional[str]
    points: Optional[int]


class RaceDetails(BaseModel):
    anet_id: int
    gender: Optional[Literal["M", "F"]]
    race_name: Optional[str]
    division: Optional[str]
    place_depth: Optional[int]
    score_depth: Optional[int]
    start_time: Optional[datetime]
    distance: Optional[int]


class RaceInfo(BaseModel):
    race_details: RaceDetails
    results: List[ResultInfoExtended] = list()
    team_scores: List[TeamScoreInfo] = list()


class MeetResultsInfo(BaseModel):
    meet_details: MeetDetails
    teams: List[TeamDetails]
    races: List[RaceInfo] = list()


class MeetResultsInfoRead(MeetResultsInfo):
    pass
