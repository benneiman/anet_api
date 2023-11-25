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


class TeamBase(SQLModel):
    anet_id: int
    name: str


class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: int


class Meet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    anet_id: int
    name: str
    location: str
    date: date


class Result(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    anet_id: int
    result: time
    distance: int
    place: int
    pb: bool
    sb: bool

    athlete_id: Optional[int] = Field(default=None, foreign_key="athlete.id")
    # athlete: Optional[Athlete] = Relationship(back_populates="results")

    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    meet_id: Optional[int] = Field(default=None, foreign_key="meet.id")
