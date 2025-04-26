from pydantic import BaseModel, EmailStr, Field


class ForgotPassword(BaseModel):
    email: EmailStr = Field(description="Электронная почта")


class ResetPassword(BaseModel):
    email: EmailStr = Field(description="Электронная почта")
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    code: str = Field(max_length=6, min_length=6, description="6-ти значный код")