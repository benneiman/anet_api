from sqlmodel import Session

from .models import Team


def create_team(session: Session, team_data: Team):
    team_item = Team(**team_data.dict())
    session.add(team_item)
    session.commit()
    session.refresh(team_item)
    return team_item
