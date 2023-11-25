from typing import Optional, List

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

from datetime import date, time


class AthleteBase(SQLModel):
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


class TeamBase(SQLModel):
    anet_id: int
    name: str


class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: int


class MeetBase(SQLModel):
    anet_id: int
    name: str
    venue: str
    address: Optional[str]
    city: str
    state: str
    zipcode: int
    date: date


class Meet(MeetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class MeetCreate(MeetBase):
    pass


class MeetRead(MeetBase):
    id: int


class ResultBase(SQLModel):
    anet_id: int
    result: time
    distance: int
    place: int
    pb: bool
    sb: bool


class Result(ResultBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    athlete_id: Optional[int] = Field(default=None, foreign_key="athlete.id")
    # athlete: Optional[Athlete] = Relationship(back_populates="results")

    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    meet_id: Optional[int] = Field(default=None, foreign_key="meet.id")


class ResultCreate(ResultBase):
    pass


class ResultRead(ResultBase):
    id: int
