from sqlmodel import Session, SQLModel

from .models import Team, Meet, Athlete, Result


def create_team(session: Session, team_data: Team):
    team_item = Team(**team_data.dict())
    session.add(team_item)
    session.commit()
    session.refresh(team_item)
    return team_item


def get_team_by_anet_id(db: Session, anet_id: int):
    return db.exec(Team).filter(Team.anet_id == anet_id).first()


def create_athlete(session: Session, athlete_data: Athlete):
    athlete_item = Athlete(**athlete_data.dict())
    session.add(athlete_item)
    session.commit()
    session.refresh(athlete_item)
    return athlete_item
