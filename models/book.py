from pydantic import BaseModel, Schema, Field
from models.author import Author
from utils.const import ISBN_DESCRIPTION


class Book(BaseModel):
    isbn: str = Field(None,description=ISBN_DESCRIPTION)
    name: str
    author: Author
    year: int = Field(None,gt=1900, lt=2100)