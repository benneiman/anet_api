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


def create_item(
    session: Session,
    create_item: TeamCreate | AthleteCreate | MeetCreate | ResultCreate | RaceCreate,
    model: Team | Athlete | Meet | Result | Race,
):
    item = model.model_validate(create_item)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_object_by_anet_id(
    session: Session, anet_id: int, obj: Athlete | Team | Result | Meet | Race
):
    try:
        statement = select(obj).where(obj.anet_id == anet_id)
    except:
        raise TypeError(
            "Only Athlete, Team, Result, Meet, or Race models can be passed"
        )
    return session.exec(statement).first()


def convert_to_seconds(race_time: str):
    c = [60, 1]
    race_time = re.sub("[a-zA-z]", "", race_time)
    print(race_time)
    t = [float(x) for x in race_time.split(":")]
    return sum([np.prod(lst) for lst in zip(c, t)])
