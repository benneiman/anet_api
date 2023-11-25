from sqlmodel import Session, create_engine
from sqlalchemy.orm import sessionmaker

SQLMODEL_DATABASE_URL = "postgresql+psycopg2:///anet_results"

engine = create_engine(SQLMODEL_DATABASE_URL)

SessionLocal = sessionmaker(engine, class_=Session)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
