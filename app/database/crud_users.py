from typing import Optional

from sqlalchemy.orm import Session

from app import schemas
from app.database import models
from app.utils import make_password_hash


def get_user_by_username(session: Session, username: str) -> Optional[models.User]:
    return (
        session.query(models.User)
        .filter(models.User.username == username)
        .one_or_none()
    )


def create_user(session: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = make_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    session.add(db_user)
    session.flush()
    return db_user
