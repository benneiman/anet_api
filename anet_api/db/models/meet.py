from typing import Optional

from sqlmodel import Field

from anet_api.db.models.base import AbstractBase

from datetime import date


class MeetBase(AbstractBase):
    anet_id: int
    meet: str
    venue: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zipcode: Optional[str]
    date: date


class Meet(MeetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class MeetCreate(MeetBase):
    pass


class MeetRead(MeetBase):
    id: int
