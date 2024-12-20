from typing import Optional

from sqlmodel import Field
from sqlalchemy.types import Double

from anet_api.db.models.base import AbstractBase

from datetime import date


class ResultBase(AbstractBase):
    anet_id: int
    distance: Optional[int]
    place: Optional[int]
    pb: Optional[bool]
    sb: Optional[bool]


class Result(ResultBase, table=True):
    result: float = Field(sa_type=Double)
    id: Optional[int] = Field(default=None, primary_key=True)

    athlete_id: Optional[int] = Field(default=None, foreign_key="athlete.id")
    # athlete: Optional[Athlete] = Relationship(back_populates="results")

    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    meet_id: Optional[int] = Field(default=None, foreign_key="meet.id")

    race_id: Optional[int] = Field(default=None, foreign_key="race.id")


class ResultCreate(ResultBase):
    anet_athlete_id: int
    anet_team_id: int
    anet_meet_id: int
    anet_race_id: int
    result: str


class ResultRead(ResultBase):
    id: int
    result: float
    team_id: int
    athlete_id: int
    meet_id: int
    race_id: int
