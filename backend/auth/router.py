from fastapi import APIRouter, status, Response, HTTPException
from .auth import get_password_hash
from .models import User, Token
from .service import UserRepository


router = APIRouter(tags=["Users 📚"])


@router.post(
    path="/register",
    summary="UserCreate registration",
    description="UserCreate registration",
    response_description="HTTP 201 STATUS",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user: User):
    user.password = get_password_hash(user.password)
    await UserRepository.add_user(user)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post(
    path="/login",
    summary="Login for user",
    description="Authorization in the application",
    response_description="Access token (Bearer) and refresh token (Cookie)",
    status_code=status.HTTP_200_OK,
    response_model=Token,
)
async def login_user(user: User):
    pass


@router.post(
    path="/refresh_token"
)
async def refresh_access_token(token: Token):
    pass