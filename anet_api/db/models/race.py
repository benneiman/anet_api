from typing import Optional

from sqlmodel import Field

from anet_api.db.models.base import AbstractBase

from datetime import datetime


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
