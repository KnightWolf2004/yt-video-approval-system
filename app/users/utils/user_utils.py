from sqlmodel import Session, select

from app.users.models.user_model import User


def get_user_by_username(session: Session, username: str):
    statement = select(User).where(User.username==username)
    user = session.exec(statement).first()
    return user