from datetime import datetime

from sqlmodel import Field, SQLModel


class AbstractBase(SQLModel):
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    last_edited: datetime = Field(default_factory=datetime.utcnow, nullable=False)
