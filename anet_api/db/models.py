from typing import Optional, Literal
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.types import Double
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION


from datetime import date, time


class AbstractBase(SQLModel):
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    last_edited: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class AthleteBase(AbstractBase):
    anet_id: int
    first_name: str
    last_name: str
    gender: str
    age: Optional[int]


class Athlete(AthleteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class AthleteCreate(AthleteBase):
    pass


class AthleteRead(AthleteBase):
    id: int

    # results: List["Result"] = Relationship(back_populates="athlete")


class AthleteUpdate(AthleteBase):
    first_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[str]
    age: Optional[int]


class TeamBase(AbstractBase):
    anet_id: int
    name: str


class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: int


class MeetBase(AbstractBase):
    anet_id: int
    meet: str
    venue: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipcode: Optional[int]
    date: date


class Meet(MeetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class MeetCreate(MeetBase):
    pass


class MeetRead(MeetBase):
    id: int


class RaceBase(AbstractBase):
    anet_id: int
    gender: Optional[str]
    race_name: Optional[str]
    division: Optional[str]
    place_depth: Optional[int]
    score_depth: Optional[int]
    start_time: Optional[datetime]
    distance: Optional[int]


class Race(RaceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class RaceCreate(RaceBase):
    pass


class RaceRead(RaceBase):
    id: int


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
