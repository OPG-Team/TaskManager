from fastapi import APIRouter, status, Response, Request, Depends, HTTPException
from .utils import get_password_hash, create_access_token, create_refresh_token
from .dependencies import refresh_access_token, get_current_user
from .models import User, Token, UserInfo
from .responses.http_errors import HTTTPError
from .responses.responses import UsersResponse, base_auth_responses
from .service import UserRepository


router = APIRouter(tags=["Users 👔"])


@router.post(
    path="/register",
    summary="UserCreate registration",
    description="UserCreate registration",
    response_description="HTTP 201 STATUS",
    responses=UsersResponse.register_post,
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
    responses=UsersResponse.login_post,
    response_model=Token,
)
async def login_user(response: Response, user: User):
    check = await UserRepository.authenticate_user(email=user.email, password=user.password)
    if check is None:
        raise HTTTPError.BAD_CREDENTIALS_400

    access_token = create_access_token(data={"sub": str(check.email), "role": str(check.role)})
    create_refresh_token(response=response, data={"sub": str(check.email), "role": str(check.role)})

    return Token(access_token=access_token, token_type="Bearer")


@router.post(
    path="/refresh_token",
    summary="Refresh access token",
    description="Refresh access token",
    response_description="Bearer Token (Access)",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    responses=UsersResponse.refresh_post,
)
async def refresh_token_point(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTTPError.BAD_CREDENTIALS_401

    email = await request.app.redis.get_refresh_token_email(refresh_token)
    if email:
        raise HTTTPError.REFRESH_TOKEN_IN_BLACK_LIST_401

    access_token = await refresh_access_token(refresh_token=refresh_token)
    return Token(access_token=access_token, token_type="Bearer")


@router.post(
    path="/logout",
    summary="Logout, add refresh_token to black list",
    description="Logout, add refresh_token to black list",
    response_description="Status code",
    status_code=status.HTTP_200_OK,
    responses=base_auth_responses,
)
async def logout(request: Request, user_data: UserInfo = Depends(get_current_user)):
    refresh_token = request.cookies.get("refresh_token")
    print(refresh_token)
    if refresh_token:
        await request.app.redis.add_refresh_token_email(user_data.email, refresh_token)
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    path="/me",
    summary="Information about you",
    description="Information about you",
    response_description="User info",
    status_code=status.HTTP_200_OK,
    response_model=UserInfo,
    responses=base_auth_responses,
)
async def get_me(user_data: UserInfo = Depends(get_current_user)):
    return user_data