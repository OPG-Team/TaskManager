from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import jwt
from fastapi import Response
from config import (
    SECRET_KEY_JWT,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hashes a given password using a secure hashing algorithm.

    Args:
        password: The plaintext password to be hashed.

    Returns:
        A str, the hashed password.
    """
    return pwd_context.hash(password)


def verify_password(default_password: str, hashed_password: str) -> bool:
    """Verifies password.

    Args:
        default_password (str): Password to check.
        hashed_password (str): Hashed password.

    Returns:
        A bool, if password success verified True, else False.
    """
    return pwd_context.verify(default_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Creates encoded access token.

    Args:
        data (dict): Information for encoding in access token.

    Returns:
        A str, encoded token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY_JWT, algorithm=ALGORITHM)
    return encode_jwt


def create_refresh_token(response: Response, data: dict) -> None:
    """Creates encoded refresh token and sets it as a cookie in the response.

    Args:
        response (Response): The HTTP response object
        data (dict): Information for encoding in access token.

    Returns:
        None
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY_JWT, algorithm=ALGORITHM)
    response.set_cookie(
        key="refresh_token",
        value=encode_jwt,
        expires=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        secure=False,
        httponly=True,
    )