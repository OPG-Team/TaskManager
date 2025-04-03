from typing import Optional
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .utils import verify_password
from .database import UserOrm, UserRole
from database import new_session
from .models import User
from .responses.http_errors import HTTPError


class UserRepository:
    @classmethod
    async def find_one_or_none_by_email(cls, email: str) -> Optional[UserOrm]:
        """Finds a user by email.

        Args:
            email: The email of the user to find.

        Returns:
            A Optional[UsersOrm], the user object if found, otherwise None.
        """
        async with new_session() as session:
            result = await session.execute(select(UserOrm).where(UserOrm.email == email))
            user = result.scalar_one_or_none()
            return user

    @classmethod
    async def add_user(cls, data: User) -> Optional[str]:
        async with new_session() as session:
            try:
                user = UserOrm(email=data.email, password=data.password, role=UserRole.DEFAULT)
                session.add(user)
                await session.flush()
                await session.commit()
                return user.email
            except IntegrityError:
                await session.rollback()
                raise HTTPError.email_already_exists_409()

    @classmethod
    async def authenticate_user(cls, email: EmailStr, password: str) -> Optional[UserOrm]:
        """Authenticates a user by email and password.

        Args:
            email: The email of the user to authenticate.
            password: The password of the user to authenticate.

        Returns:
            A Optional[UserOrm], the user object if authentication is successful, otherwise None.
        """
        user = await cls.find_one_or_none_by_email(str(email))
        if not user or verify_password(default_password=password, hashed_password=str(user.password)) is False:
            return None
        return user
