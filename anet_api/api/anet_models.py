from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import date


class ScheduleInfo(BaseModel):
    anet_id: int
    meet: str
    venue: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipcode: Optional[int]
    date: Optional[date]


class RosterInfo(BaseModel):
    anet_id: int
    first_name: str
    last_name: str
    gender: Literal["M", "F"]
    age: Optional[int]


class TeamDetails(BaseModel):
    name: Optional[str]
    city: Optional[str]
    state: Optional[str]
    mascot: Optional[str]


class TeamInfo(BaseModel):
    team_data: TeamDetails
    roster: List[RosterInfo] = list()
    schedule: List[ScheduleInfo] = list()


class TeamInfoRead(TeamInfo):
    pass


class ResultInfo(BaseModel):
    anet_id: int
    anet_meet_id: Optional[int]
    anet_team_id: Optional[int]
    anet_athlete_id: Optional[int]
    first_name: Optional[str]
    last_name: Optional[str]
    team: Optional[str]
    grade: Optional[int]
    result: str
    place: Optional[int]
    pb: Optional[bool]
    sb: Optional[bool]


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
