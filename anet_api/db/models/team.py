from typing import Optional

from sqlmodel import Field

from anet_api.db.models.base import AbstractBase


class TeamBase(AbstractBase):
    anet_id: int
    name: str


class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: int
