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
    Race,
    RaceCreate,
)


def create_team(session: Session, team: TeamCreate):
    team_item = Team.model_validate(team)
    session.add(team_item)
    session.commit()
    session.refresh(team_item)
    return team_item


def create_athlete(session: Session, athlete: AthleteCreate):
    athlete_item = Athlete.model_validate(athlete)
    session.add(athlete_item)
    session.commit()
    session.refresh(athlete_item)
    return athlete_item


def create_meet(session: Session, meet: MeetCreate):
    meet_item = Meet.model_validate(meet)
    session.add(meet_item)
    session.commit()
    session.refresh(meet_item)
    return meet_item


def create_result(session: Session, result: ResultCreate):
    result_item = Result.model_validate(result)
    session.add(result_item)
    session.commit()
    session.refresh(result_item)
    return result_item


def get_object_by_anet_id(
    session: Session, anet_id: int, obj: Athlete | Team | Result | Meet | Race
):
    statement = select(obj).where(obj.anet_id == anet_id)
    return session.exec(statement).first()


def create_race(session: Session, race: RaceCreate):
    race_item = Race.model_validate(race)
    session.add(race_item)
    session.commit()
    session.refresh(race_item)
    return race_item


def convert_to_seconds(race_time: str):
    c = [60, 1]
    race_time = re.sub("[a-zA-z]", "", race_time)
    print(race_time)
    t = [float(x) for x in race_time.split(":")]
    return sum([np.prod(lst) for lst in zip(c, t)])
