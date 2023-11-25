from sqlmodel import Session, SQLModel, select

from . import Team, TeamCreate, Meet, Athlete, AthleteCreate, Result


def create_team(session: Session, team: TeamCreate):
    team_item = Team.from_orm(team)
    session.add(team_item)
    session.commit()
    session.refresh(team_item)
    return team_item


def get_team_by_anet_id(session: Session, anet_id: int):
    statement = select(Team).where(Team.anet_id == anet_id)
    return session.exec(statement).first()


def create_athlete(session: Session, athlete: AthleteCreate):
    athlete_item = Athlete.from_orm(athlete)
    session.add(athlete_item)
    session.commit()
    session.refresh(athlete_item)
    return athlete_item


def get_athlete_by_anet_id(session: Session, anet_id: int):
    statement = select(Athlete).where(Athlete.anet_id == anet_id)
    return session.exec(statement).first()
