from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import DeclarativeBase


class User(DeclarativeBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    bots = relationship(
        'Bot', back_populates='user', cascade='all, delete', passive_deletes=True
    )


class Bot(DeclarativeBase):
    __tablename__ = 'bots'

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('User', back_populates='bots', uselist=False)
