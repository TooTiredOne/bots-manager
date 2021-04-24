from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class BotBase(BaseModel):
    pass


class BotCreate(BotBase):
    token: str


class Bot(BotCreate):
    id: int

    class Config:
        orm_mode = True
