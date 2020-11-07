from functools import cached_property, lru_cache
from typing import Optional

import aioredis
from async_property import async_cached_property
from async_property.cached import AsyncCachedPropertyDescriptor
from pydantic import BaseSettings
from databases import Database
from utils.const import DB_URL, REDIS_URL  # TESTING, TEST_DB_URL, IS_LOAD_TEST, IS_PRODUCTION, DB_URL_PRODUCTION


class Settings(BaseSettings):

    @async_cached_property
    async def redis(self):
        return await aioredis.create_redis_pool(REDIS_URL)

    @cached_property
    def database(self):
        return Database(DB_URL)

    class Config:
        env_file = ".env"
        keep_untouched = (cached_property, AsyncCachedPropertyDescriptor)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

# if TESTING or IS_LOAD_TEST:
#     db = Database(TEST_DB_URL)
# elif IS_PRODUCTION:
#     db = Database(DB_URL_PRODUCTION)
# else:
#
