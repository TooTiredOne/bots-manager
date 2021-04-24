import os

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

import app.routing.bots as bots_routing
import app.routing.users as users_routing
from app.database import models
from app.database.db import engine
from app.dependencies import UnauthorizedException

# project structure was based on one of my previous works'

PORT = int(os.environ.get('PORT', '8000'))
models.DeclarativeBase.metadata.create_all(bind=engine)
app = FastAPI()


@app.exception_handler(UnauthorizedException)
def unauthorized_exception_handler(
    _request: Request, _exc: UnauthorizedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': 'Incorrect username or password'},
        headers={'WWW-Authenticate': 'Basic'},
    )


app.include_router(
    users_routing.router,
    prefix='/api/v1/users',
    tags=['users'],
)

app.include_router(
    bots_routing.router,
    prefix='/api/v1/bots',
    tags=['bots'],
)


@app.get('/')
async def index() -> str:
    return 'documentation is available on /docs'


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=PORT, reload=True)
