from typing import Optional
import redis.asyncio as redis
from config import REFRESH_TOKEN_EXPIRE_DAYS


class RedisDB:
    """
    Class for working with Redis
    """
    def __init__(self, url: str) -> None:
        self.__redis_connect = redis.from_url(url=url)

    async def add_refresh_token_email(self, email: str, refresh_token: str) -> None:
        await self.__redis_connect.setex(refresh_token, REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, email)

    async def get_refresh_token_email(self, refresh_token: str) -> Optional[str]:
        email = await self.__redis_connect.get(refresh_token)

        if email:
            return email.decode('utf-8')

        return None

    async def del_email_refresh_token(self, email: str) -> None:
        await self.__redis_connect.delete(email)

    async def close(self) -> None:
        await self.__redis_connect.close()