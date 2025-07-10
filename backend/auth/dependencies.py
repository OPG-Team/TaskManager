from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.models import UserInfo
from auth.jwt import JWTService


http_bearer = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> UserInfo:
    """Retrieves the current user based on the provided JWT token.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials containing the JWT token.

    Returns:
        UserInfo, The user object corresponding to the valid JWT token.
    """
    token = credentials.credentials

    user = await JWTService.descript_and_validate_token(token)

    return UserInfo.model_validate(user.__dict__)