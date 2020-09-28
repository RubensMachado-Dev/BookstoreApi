import enum
from pydantic import BaseModel

from fastapi import Query
from typing import List

class Author(BaseModel):
    name: str
    book: List[str]
