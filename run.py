import uvicorn
from fastapi import FastAPI, Body, Header, File, Depends, HTTPException
from routes.v1 import app_v1
from passlib.context import CryptContext
from starlette.responses import Response
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from utils.config import Settings, get_settings
from utils.security import authenticate_user, create_jwt_token, check_jwt_token
from models.jwt_user import JWTUser
from utils.config import cached_property
from utils.redis_object import redis
import aioredis
from utils.const import (
    TOKEN_DESCRIPTION,
    TOKEN_SUMMARY,
    REDIS_URL, DB_URL,
    # TESTING,
    # IS_PRODUCTION,
    # REDIS_URL_PRODUCTION,
    # TOKEN_INVALID_CREDENTIALS_MSG,
)

app = FastAPI(title="Bookstore API documentation", description="It is an API used for a Bookstore", version='1.0')

# app.mount("/v1", app_v1)
app.include_router(app_v1, prefix="/v1", dependencies=[Depends(check_jwt_token)])


@app.on_event("startup")
async def connect_db():
    settings = get_settings()
    # if not TESTING:
    #     await db.connect()
    #     if IS_PRODUCTION:
    #         re.redis = await aioredis.create_redis_pool(REDIS_URL_PRODUCTION)
    #     else:
    #         re.redis = await aioredis.create_redis_pool(REDIS_URL)

    await settings.database.connect()
    await settings.redis

@app.on_event("shutdown")
async def disconnect_db():
    settings = get_settings()
    # if not TESTING:
    #     await db.disconnect()
    #
    #     re.redis.close()
    #     await re.redis.wait_closed()
    await settings.database.disconnect()
    await settings.redis.closed()
    await settings.wait_closed()


@app.get("/")
async def health_check():
    return {"OK"}


@app.post("/token", description=TOKEN_DESCRIPTION, summary=TOKEN_SUMMARY)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    jwt_user_dict = {"username": form_data.username, "password": form_data.password}
    jwt_user = JWTUser(**jwt_user_dict)
    user = await authenticate_user(jwt_user)
    if user is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    jwt_token = create_jwt_token(user)
    return {"access_token": jwt_token}


@app.middleware("http")
async def middleware(request: Request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    # modify response
    execution_time = (datetime.utcnow() - start_time).microseconds
    response.headers["x-execution-time"] = str(execution_time)
    return response


if __name__ == "__main__":
    uvicorn.run("run:app",port=8000, reload=True)
