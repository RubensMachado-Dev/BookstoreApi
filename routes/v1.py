from fastapi import FastAPI, Body, Header, File, Depends, HTTPException, APIRouter
from models.user import User
from models.author import Author
from models.book import Book
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from starlette.responses import Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from utils.security import authenticate_user, create_jwt_token, check_jwt_token
from models.jwt_user import JWTUser

#app_v1 = FastAPI(openapi_prefix="/v1")
app_v1= APIRouter()

@app_v1.post("/user", status_code=HTTP_201_CREATED)
async def post_user(user: User, x_custom: str = Header("Default")):
    return {"Request body": user, "Request Header": x_custom}


@app_v1.get("/user")
async def get_user_validation(password: str):
    return {"query parameter": password}


@app_v1.get(
    "/book/{isbn}",
    response_model=Book,
    response_model_include ={"name", "year"},
)
async def get_book_with_isbn(isbn: str):
    author_dict = {
        "name": "author1",
        "book": ["book1", "book2"]
    }
    author1 = Author(**author_dict)
    example = {
        "isbn": "isbn1",
        "name": "book1",
        "year": 2019,
        "author": author1
    }
    book1 = Book(**example)
    return book1


@app_v1.get("/book/{isbn}")
async def get_book_with_isbn(isbn: str):
    return {"Query changeable ": isbn}


@app_v1.get("/author/{id}/book")
async def get_authors_books(id: int, category: str, order: str = "asc", ):
    return {"Query changeable ": order + category + str(id)}


@app_v1.patch("/author/name")
async def patch_author_name(name: str = Body(..., embed=True)):
    return {"name in body": name}


@app_v1.post("/user/author/")
async def post_user_and_author(user: User, author: Author, bookstore_name: str = Body(..., embed=True)):
    return {"user": user, "author": author, "bookstore": bookstore_name}


@app_v1.post("/user/photo/")
async def upload_user_photo(response: Response, profile_photo: bytes = File(...), ):
    response.headers["x-file-size"] = str(len(profile_photo))
    response.set_cookie(key="cookie-api", value="test")
    return {"file_size": len(profile_photo)},


