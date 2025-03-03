from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    email: EmailStr = Field(description="Электронная почта")
    password: str = Field(min_length=6, max_length=50, description="Пароль, от 6 до 50 знаков")


class UserRead(BaseModel):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str