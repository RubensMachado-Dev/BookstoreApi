from passlib.context import CryptContext
from models.jwt_user import JWTUser
from datetime import datetime, timedelta
from utils.const import (
    JWT_EXPIRATION_TIME_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
   #WT_EXPIRED_MSG,
   #JWT_INVALID_MSG,
   # JWT_WRONG_ROLE,
)
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import time
#from utils.db_functions import db_check_token_user, db_check_jwt_username
from starlette.status import HTTP_401_UNAUTHORIZED

pwd_context = CryptContext(schemes=["bcrypt"])
oauth_schema = OAuth2PasswordBearer(tokenUrl="/token")

jwt_user1={"username": 'user1',
           "password": "$2b$12$Qy/1SW8dLBUrWvDq3OdVaOsAJigkodApMmgiQ02n6yOevtRKKMnYS",
           "disabled":False,
           "role":"personel",
           }
fake_jwt_user1= JWTUser(**jwt_user1)



def get_hashed_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(e)
        return False
print(get_hashed_password("pass1"))

# Authenticate username and password to give JWT token
def authenticate_user(user: JWTUser):
    # potential_users = await db_check_token_user(user)
    # is_valid = False
    # for db_user in potential_users:
    #     if verify_password(user.password, db_user["password"]):
    #         is_valid = True
    if fake_jwt_user1.username == user.username:
        if verify_password(user.password,fake_jwt_user1.password):
            user.role="admin"
   # if is_valid:
        #user.role = "admin"
            return user

    return None


# Create access JWT token
def create_jwt_token(user: JWTUser):
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    jwt_payload = {"sub": user.username, "role": user.role, "exp": expiration}
    jwt_token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return jwt_token


# Check whether JWT token is correct
async def check_jwt_token(token: str = Depends(oauth_schema)):
    try:
        jwt_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        username = jwt_payload.get("sub")
        role = jwt_payload.get("role")
        expiration = jwt_payload.get("exp")
        if time.time() < expiration:
            if fake_jwt_user1.username== username:
            # is_valid = await db_check_jwt_username(username)
            #if is_valid:
                return final_checks(role)
            else:
                return False
                # raise HTTPException(
                #     status_code=HTTP_401_UNAUTHORIZED#, detail=JWT_INVALID_MSG
                # )
        else:
            return False
            # raise HTTPException(
            #     status_code=HTTP_401_UNAUTHORIZED#, detail=JWT_EXPIRED_MSG
            # )
    except Exception as e:
        return False
        # raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


# Last checking and returning the final result
def final_checks(role: str):
    if role == "admin":
        return True
    else:
        return False
        # raise HTTPException(status_code=HTTP_401_UNAUTHORIZED#, detail=JWT_WRONG_ROLE
        #  )

