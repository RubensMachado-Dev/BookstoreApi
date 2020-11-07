import pickle

from fastapi import FastAPI, Body, Header, File, Depends, HTTPException, APIRouter
from models.user import User
from models.author import Author
from models.book import Book
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from starlette.responses import Response

from utils.config import get_settings, Settings
from utils.db_functions import db_insert_personel, db_check_personel, db_get_book_with_isbn, db_get_author, \
    db_get_author_from_id, db_patch_author_name
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#from utils.redis_object import redis
from utils.helper_functions import upload_image_to_server
from utils.redis_object import redis as re
from utils.security import authenticate_user, create_jwt_token, check_jwt_token
from models.jwt_user import JWTUser
#app_v1 = FastAPI(openapi_prefix="/v1")
app_v1= APIRouter()


@app_v1.post("/user", status_code=HTTP_201_CREATED, tags=["User"])
async def post_user(user: User):
    await db_insert_personel(user)
    return {"result": "personel is created"}


@app_v1.post("/login", tags=["User"])
async def get_user_validation(settings: Settings = Depends(get_settings),username: str = Body(...), password: str = Body(...)):
    #result= await db_check_personel(username,password)
    redis_key = f"{username},{password}"
    result = await settings.redis.get(redis_key)

    # Redis has the data
    if result:
        if result == "true":
            return {"is_valid (redis)": True}
        else:
            return {"is_valid (redis)": False}
    # Redis does not have the data
    else:
        result = await db_check_personel(username, password)
        if result is None:
            return {"is_valid":None}
        else:
            await settings.redis.set(redis_key, str(result))
            return {"is_valid(db)": result}

@app_v1.get(
            "/book/{isbn}",
            response_model=Book,
            response_model_include ={"name", "year"},
            tags=["Book"]
            )
async def get_book_with_isbn(isbn: str,settings: Settings = Depends(get_settings)):
    result = await settings.redis.get(isbn)

    if result:
        result_book = pickle.loads(result)
        return result_book
    else:
        book = await db_get_book_with_isbn(isbn)
        author = await db_get_author(book["author"])
        author_obj = Author(**author)
        book["author"] = author_obj
        result_book = Book(**book)

        await settings.redis.set(isbn, pickle.dumps(result_book))
        return result_book
    # print("aqui")
    # print(isbn)
    # print("aqui")
    # book= await db_get_book_with_isbn(isbn)
    # author=await db_get_author(book["author"])
    # author_obj=Author(**author)
    # book["author"]= author_obj
    # result_book = Book(**book)
    # return result_book


# @app_v1.get("/book/{isbn}",response_model=Book,response_model_include={"name","year"},tags=["Book"])
# async def get_book_with_isbn(isbn: str):
#     return {"Query changeable ": isbn}


@app_v1.get("/author/{id}/book",tags=["Book"])
async def get_authors_books(id: int, order: str = "asc" ):
    author = await db_get_author_from_id(id)
    if author is not None:
        books = author["books"]
        if order =="asc":
            books =sorted(books)
        else:
            books =sorted(books, reverse=True)
        return {"books":books}
    else:
        return ("No author with corresponding ID")

@app_v1.patch("/author/{id}/name")
async def patch_author_name(id:int,name: str = Body(..., embed=True)):
    await db_patch_author_name(id,name)
    return {"Result":"name is updated"}


@app_v1.post("/user/author/")
async def post_user_and_author(user: User, author: Author, bookstore_name: str = Body(..., embed=True)):
    return {"user": user, "author": author, "bookstore": bookstore_name}


@app_v1.post("/user/photo/")
async def upload_user_photo(response: Response, profile_photo: bytes = File(...), ):
    await upload_image_to_server(profile_photo)
    return {"file_size": len(profile_photo)},


