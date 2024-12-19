from sqlmodel import Session, create_engine
from sqlalchemy.orm import sessionmaker

from settings import DB_URL

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(engine, class_=Session)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
