from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import schemas
from app.database import crud_users as crud
from app.database import models
from app.dependencies import get_session

router = APIRouter()


class UsernameAlreadyTaken(HTTPException):
    def __init__(self, **kwargs: Dict[Any, Any]):
        super().__init__(status_code=409, detail='Username already taken', **kwargs)


@router.post(
    '',
    tags=['users'],
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary='Register new user',
)
def create_user(
    user: schemas.UserCreate, session: Session = Depends(get_session)
) -> models.User:
    db_user = crud.get_user_by_username(session=session, username=user.username)
    if db_user:
        raise UsernameAlreadyTaken
    try:
        return crud.create_user(session=session, user=user)
    except IntegrityError as err:
        raise UsernameAlreadyTaken from err
