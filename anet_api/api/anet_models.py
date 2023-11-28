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
    team_data: dict
    roster: List[RosterInfo] = list()
    schedule: List[ScheduleInfo] = list()


class TeamInfoRead(TeamInfo):
    pass
