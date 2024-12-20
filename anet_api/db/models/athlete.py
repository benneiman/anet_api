from typing import Optional

from sqlmodel import Field

from anet_api.db.models.base import AbstractBase


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
