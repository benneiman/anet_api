from typing import Optional, List

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

from datetime import date, time


class Athlete(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    anet_id: int
    name: str
    gender: str

    results: List["Result"] = Relationship(back_populates="athlete")


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    anet_id: int
    name: str


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
    place: int

    athlete_id: Optional[int] = Field(default=None, foreign_key="athlete.id")
    athlete: Optional[Athlete] = Relationship(back_populates="results")

    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    meet_id: Optional[int] = Field(default=None, foreign_key="meet.id")


db_name = "anet_results"
db_string = f"postgresql:///{db_name}"

engine = create_engine(db_string, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "main":
    create_db_and_tables()
