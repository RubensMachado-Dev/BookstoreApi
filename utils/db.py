import asyncio
from databases import Database
from fastapi import Depends

from utils.const import DB_URL
from utils.config import get_settings, Settings


async def execute(query, is_many, values=None,db: Settings = Depends(get_settings)):
    db = get_settings()
    if is_many:
        await db.database.execute_many(query=query,values=values)
    else:
        await db.database.execute(query=query,values=values)


async def fetch(query, is_one, values=None):
    db= get_settings()
    if is_one:
        result= await db.database.fetch_one(query=query,values=values)
        if result is None:
            return None
        else:
            out = dict(result)
    else:
        result = await db.database.fetch_all(query=query,values = values)
        out=[]
        for row in result:
            out.append(dict(row))
    print(out)
    return out

# async def test_orm():
#     query=authors.insert().values(id=2,name="author2",books=["book3", "book4"])
#     await execute(query,False)

#loop =asyncio.get_event_loop()
#loop.run_until_complete(test_orm())