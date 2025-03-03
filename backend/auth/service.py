from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from .database import UserOrm, UserRole
from database import new_session
from .models import User


class UserRepository:
    @staticmethod
    async def add_user(data: User):
        async with new_session() as session:
            try:
                user = UserOrm(email=data.email, password=data.password, role=UserRole.DEFAULT)
                session.add(user)
                await session.flush()
                await session.commit()
                return user.email
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=status.HTTP_409_CONFLICT)