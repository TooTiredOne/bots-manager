from typing import List, Optional

from sqlalchemy.orm import Session

from app import schemas
from app.database import models


def get_number_of_bots(user_id: int, session: Session) -> int:
    return len(session.query(models.Bot).filter(models.Bot.user_id == user_id).all())


def get_users_bot_by_token(
    user_id: int, token: str, session: Session
) -> Optional[models.Bot]:
    return (
        session.query(models.Bot)
        .filter(models.Bot.token == token)
        .filter(models.Bot.user_id == user_id)
        .one_or_none()
    )


def get_bot_by_token(token: str, session: Session) -> Optional[models.Bot]:
    return session.query(models.Bot).filter(models.Bot.token == token).one_or_none()


def get_users_bot_by_id(
    user_id: int, bot_id: int, session: Session
) -> Optional[models.Bot]:
    return (
        session.query(models.Bot)
        .filter(models.Bot.id == bot_id)
        .filter(models.Bot.user_id == user_id)
        .one_or_none()
    )


def add_bot(user_id: int, bot: schemas.BotCreate, session: Session) -> models.Bot:
    db_bot = models.Bot(token=bot.token, user_id=user_id)
    session.add(db_bot)
    session.flush()
    return db_bot


def get_users_bots(user_id: int, session: Session) -> List[models.Bot]:
    return session.query(models.Bot).filter(models.Bot.user_id == user_id).all()


def delete_bot(bot_id: int, session: Session) -> None:
    session.query(models.Bot).filter(models.Bot.id == bot_id).delete()
    session.flush()
