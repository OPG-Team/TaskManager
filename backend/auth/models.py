from pydantic import BaseModel, Field, EmailStr, ConfigDict
from auth.database import UserRole, ConnectionType


class User(BaseModel):
    email: EmailStr = Field(description="Электронная почта")
    password: str = Field(min_length=6, max_length=50, description="Пароль, от 6 до 50 знаков")


class UserInfo(BaseModel):
    email: EmailStr
    password: str
    is_active: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class ConnectionWithUser(BaseModel):
    type: ConnectionType
    user: UserInfo

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str