import enum
from pydantic import BaseModel
from fastapi import Query


class Role(str, enum.Enum):
    admin: str = "admin"
    personel: str = "personel"


class User(BaseModel):
    name: str = "default"
    password: str
    mail: str = Query(...,
                      regex="^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})$")
    role: Role
