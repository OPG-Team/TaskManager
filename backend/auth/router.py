from fastapi import APIRouter, status, Response, Request, Depends
from utils import handle_catch_error
from .utils import get_password_hash
from .dependencies import get_current_user
from .models import User, Token, UserInfo
from .responses.http_errors import HTTPError
from .responses.responses import UsersResponse, base_auth_responses
from .service import UserRepository
from .jwt import JWTService


router = APIRouter(prefix="/auth", tags=["Users 👔"])


@router.post(
    path="/register",
    summary="Register new user",
    description="Creates new user account. Hashes password automatically. Email must be unique.",
    response_description="Empty response (status 200)",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    responses=UsersResponse.register_post,
)
@handle_catch_error
async def register_user(user: User):
    user.password = get_password_hash(user.password)
    await UserRepository.add_user(user)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post(
    path="/login",
    summary="User login",
    description="Authenticates user and returns JWT tokens. Sets refresh token as HTTP-only cookie.",
    response_description="Access token (Bearer) and refresh token (Cookie)",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    responses=UsersResponse.login_post,
)
@handle_catch_error
async def login_user(response: Response, user: User):
    check = await UserRepository.authenticate_user(email=user.email, password=user.password)
    if check is None:
        raise HTTPError.bad_credentials_400()

    access_token = JWTService.create_access_token(data={"sub": str(check.email), "role": str(check.role)})
    JWTService.create_refresh_token(response=response, data={"sub": str(check.email), "role": str(check.role)})

    return Token(access_token=access_token, token_type="Bearer")


@router.post(
    path="/refresh_token",
    summary="Refresh access token",
    description="Generates new access token using valid refresh token. Does not extend refresh token lifespan.",
    response_description="Bearer Token (Access)",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    responses=UsersResponse.refresh_post,
)
@handle_catch_error
async def refresh_token_point(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPError.bad_credentials_401()

    email = await request.app.redis.get_refresh_token_email(refresh_token)
    if email:
        raise HTTPError.refresh_token_in_black_list_401()

    access_token = await JWTService.refresh_access_token(refresh_token=refresh_token)
    return Token(access_token=access_token, token_type="Bearer")


@router.post(
    path="/logout",
    summary="Logout, add refresh_token to black list",
    description="Invalidates refresh token by adding it to blacklist. Requires valid access token.",
    response_description="Empty response (status 200)",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses=base_auth_responses,
)
@handle_catch_error
async def logout(request: Request, user_data: UserInfo = Depends(get_current_user)):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await request.app.redis.add_refresh_token_email(user_data.email, refresh_token)
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    path="/me",
    summary="Information about you",
    description="Returns authenticated user's profile data. Requires valid access token.",
    response_description="User info",
    status_code=status.HTTP_200_OK,
    response_model=UserInfo,
    responses=base_auth_responses,
)
@handle_catch_error
async def get_me(user_data: UserInfo = Depends(get_current_user)):
    return user_data