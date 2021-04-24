import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import crud_bots as crud
from app.database import models
from app.dependencies import get_current_user, get_session

# code for echo was based on the following article
# https://habr.com/ru/post/322078/#content

HOSTNAME = 'another-bots-manager.herokuapp.com'
WEBHOOK_DIR = 'echo'
HOST_WEBHOOK = f'https://{HOSTNAME}/' + 'api/v1/bots/' + WEBHOOK_DIR
router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BotsLimitExceeded(HTTPException):
    def __init__(self, **kwargs: Dict[Any, Any]):
        super().__init__(status_code=409, detail='User already has 5 bots', **kwargs)


class BotAlreadyAdded(HTTPException):
    def __init__(self, **kwargs: Dict[Any, Any]):
        super().__init__(status_code=409, detail='User already has that bot', **kwargs)


class BotNotFound(HTTPException):
    def __init__(self, **kwargs: Dict[Any, Any]):
        super().__init__(
            status_code=404, detail='Bot with given id is not found', **kwargs
        )


async def make_echo_bot(token: str) -> None:
    logger.info('Connecting to tg api with token: %s', token)

    set_webhook_url = f'https://api.telegram.org/bot{token}/setWebhook'
    headers = {'Content-Type': 'application/json'}
    body = {'url': HOST_WEBHOOK + '/' + token}
    async with httpx.AsyncClient() as client:
        response = await client.post(set_webhook_url, headers=headers, json=body)
        logger.info('response from tg: %s', response.json())
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Couldn't register bot"
            )


@router.post(
    '',
    response_model=schemas.Bot,
    status_code=status.HTTP_201_CREATED,
    tags=['bots'],
    summary='Add new bot',
)
async def add_bot(
    bot: schemas.BotCreate,
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_user),
) -> Optional[models.Bot]:
    logger.info('Adding a new bot for user_id: %d', current_user.id)
    bots_num = crud.get_number_of_bots(user_id=current_user.id, session=session)
    logger.info('Current number of bots: %d', bots_num)
    if bots_num >= 5:
        logger.info('More than 5, throwing an error')
        raise BotsLimitExceeded

    db_bot = crud.get_users_bot_by_token(
        user_id=current_user.id, token=bot.token, session=session
    )
    if db_bot:
        logger.info('Bot is already added, throwing an error')
        raise BotAlreadyAdded

    await make_echo_bot(bot.token)

    return crud.add_bot(bot=bot, user_id=current_user.id, session=session)


@router.get(
    '', response_model=List[schemas.Bot], summary="Get current user's list of bots"
)
def get_all_bots(
    session: Session = Depends(get_session),
    current_user: schemas.User = Depends(get_current_user),
) -> List[models.Bot]:
    return crud.get_users_bots(user_id=current_user.id, session=session)


@router.delete('/{bot_id}', summary='Delete bot with given id')
def remove_bot(
    bot_id: int,
    current_user: schemas.User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Optional[int]:
    db_bot = crud.get_users_bot_by_id(
        user_id=current_user.id, bot_id=bot_id, session=session
    )
    if not db_bot:
        raise BotNotFound

    crud.delete_bot(bot_id=bot_id, session=session)
    return bot_id


@router.post(
    '/' + WEBHOOK_DIR + '/{bot_token}',
    status_code=status.HTTP_200_OK,
    summary='To accept messages from tg servers',
)
async def echo(
    request: Request, bot_token: str, session: Session = Depends(get_session)
) -> int:
    data = await request.json()
    logger.info('Got webhook request: %s', data)
    if 'message' in data:
        headers = {'Content-Type': 'application/json'}
        body = {
            'chat_id': data['message']['chat']['id'],
            'text': data['message']['text'],
        }

        api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

        logger.info('Checking if the bot exists')
        db_bot = crud.get_bot_by_token(bot_token, session)
        if not db_bot:
            raise BotNotFound

        async with httpx.AsyncClient() as client:
            logger.info('Send echo request to tg api')
            res = await client.post(api_url, headers=headers, json=body)
            logger.info('response for echo request: %s', res.json())
            try:
                assert res.status_code == 200
            except AssertionError as err:
                raise HTTPException(status_code=500) from err

    return status.HTTP_200_OK
