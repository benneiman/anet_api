import numpy as np
import re

from sqlmodel import Session, SQLModel, select

from . import (
    Team,
    TeamCreate,
    Meet,
    MeetCreate,
    Athlete,
    AthleteCreate,
    Result,
    ResultCreate,
)


def create_team(session: Session, team: TeamCreate):
    team_item = Team.from_orm(team)
    session.add(team_item)
    session.commit()
    session.refresh(team_item)
    return team_item


def get_team_by_anet_id(session: Session, anet_id: int):
    statement = select(Team).where(Team.anet_id == anet_id)
    return session.exec(statement).first()


def create_athlete(session: Session, athlete: AthleteCreate):
    athlete_item = Athlete.from_orm(athlete)
    session.add(athlete_item)
    session.commit()
    session.refresh(athlete_item)
    return athlete_item


def get_athlete_by_anet_id(session: Session, anet_id: int):
    statement = select(Athlete).where(Athlete.anet_id == anet_id)
    return session.exec(statement).first()


def create_meet(session: Session, meet: MeetCreate):
    meet_item = Meet.from_orm(meet)
    session.add(meet_item)
    session.commit()
    session.refresh(meet_item)
    return meet_item


def get_meet_by_anet_id(session: Session, anet_id: int):
    statement = select(Meet).where(Meet.anet_id == anet_id)
    return session.exec(statement).first()


def create_result(session: Session, result: ResultCreate):
    result_item = Result.from_orm(result)
    session.add(result_item)
    session.commit()
    session.refresh(result_item)
    return result_item


def get_result_by_anet_id(session: Session, anet_id: int):
    statement = select(Result).where(Result.anet_id == anet_id)
    return session.exec(statement).first()


def convert_to_seconds(race_time: str):
    c = [60, 1]
    race_time = re.sub("[a-zA-z]", "", race_time)
    t = race_time.split(":")
    return sum([np.prod(lst) for lst in zip(c, t)])
