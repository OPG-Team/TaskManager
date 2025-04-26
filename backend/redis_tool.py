from typing import Optional
import redis.asyncio as redis
from config import (
    REFRESH_TOKEN_EXPIRE_DAYS,
    PASSWORD_RESET_CODE_EXPIRE_MINUTES
)


class RedisTools:
    """
    Class for working with Redis
    """
    def __init__(self, url: str) -> None:
        self.__redis_connect = redis.from_url(url=url)

    async def ping(self):
        await self.__redis_connect.ping()

    # -------------------- Refresh Token --------------------
    async def add_refresh_token_email(self, email: str, refresh_token: str) -> None:
        await self.__redis_connect.setex(refresh_token, REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, email)

    async def get_refresh_token_email(self, refresh_token: str) -> Optional[str]:
        email = await self.__redis_connect.get(refresh_token)
        return email.decode('utf-8') if email else None

    async def del_email_refresh_token(self, email: str) -> None:
        await self.__redis_connect.delete(email)

    # -------------------- Password --------------------
    async def add_password_reset_code(self, email: str, code: str) -> None:
        key = f"password_reset:{email}"
        await self.__redis_connect.setex(key, PASSWORD_RESET_CODE_EXPIRE_MINUTES * 60, code)

    async def get_password_reset_code(self, email: str) -> Optional[str]:
        key = f"password_reset:{email}"
        code = await self.__redis_connect.get(key)
        return code.decode('utf-8') if code else None

    async def delete_password_reset_code(self, email: str) -> None:
        key = f"password_reset:{email}"
        await self.__redis_connect.delete(key)

    async def close(self) -> None:
        await self.__redis_connect.close()