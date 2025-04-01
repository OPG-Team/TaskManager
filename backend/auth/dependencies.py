from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError
from auth.utils import create_access_token
from auth.database import UserOrm
from auth.models import UserInfo
from auth.responses.http_errors import HTTPError
from auth.service import UserRepository
from config import SECRET_KEY_JWT, ALGORITHM


http_bearer = HTTPBearer()


async def descript_and_check_token(token: str) -> UserOrm:
    """Decodes and validates a JWT token, retrieves the corresponding user, and checks the user's status.

    Args:
        token (str): The JWT token to be decoded and validated.

    Returns:
        A UsersOrm, the user object corresponding to the validated token.

    Raises:
        HTTTPError.BAD_CREDENTIALS_403: If the token has expired.
        HTTTPError.INVALID_TOKEN_401: If the token is invalid or does not contain a user ID.
        HTTTPError.DATA_OUT_OF_DATE_403: If the user corresponding to the token does not exist.
        HTTTPError.USER_NOT_ACTIVE_403: If the user corresponding to the token is not active.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY_JWT, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPError.BAD_CREDENTIALS_403
    except JWTError:
        raise HTTPError.INVALID_TOKEN_401

    user_email = payload.get('sub')
    if not user_email:
        raise HTTPError.INVALID_TOKEN_401

    user = await UserRepository.find_one_or_none_by_email(user_email)
    if not user:
        raise HTTPError.DATA_OUT_OF_DATE_403

    if not user.is_active:
        raise HTTPError.USER_NOT_ACTIVE_403

    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> UserInfo:
    """Retrieves the current user based on the provided JWT token.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials containing the JWT token.

    Returns:
        UserInfo: The user object corresponding to the valid JWT token.
    """
    token = credentials.credentials

    user = await descript_and_check_token(token)

    return UserInfo.model_validate(user.__dict__)


async def refresh_access_token(refresh_token: str) -> str:
    """Refreshes the access token using a provided refresh token.

    Args:
        refresh_token (str): The refresh token used to generate a new access token.

    Returns:
        A str, new access token.
    """
    user = await descript_and_check_token(refresh_token)

    new_access_token = create_access_token({"sub": str(user.email), "role": str(user.role)})
    return new_access_token