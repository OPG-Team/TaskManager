from .http_errors import HTTPError
from fastapi import status
from .utils import convert_to_example


base_auth_responses = {
    status.HTTP_401_UNAUTHORIZED: convert_to_example([
        HTTPError.BAD_CREDENTIALS_401,
        HTTPError.INVALID_TOKEN_401,
    ]),
    status.HTTP_403_FORBIDDEN: convert_to_example([
        HTTPError.BAD_CREDENTIALS_403,
        HTTPError.USER_NOT_ACTIVE_403,
        HTTPError.DATA_OUT_OF_DATE_403,
    ]),
    status.HTTP_500_INTERNAL_SERVER_ERROR: convert_to_example([
        HTTPError.ENDPOINT_NOT_FOUND_500,
    ]),
}
"""Base authorization responses."""


class UsersResponse:
    """Users responses.

    Attributes:
        register_post: Responses for register
        login_post: Responses for login
        refresh_post: Responses for refresh token
    """
    register_post = {
        status.HTTP_409_CONFLICT: convert_to_example([
            HTTPError.EMAIL_ALREADY_EXISTS_409,
        ]),
    }

    login_post = {
        status.HTTP_400_BAD_REQUEST: convert_to_example([
            HTTPError.BAD_CREDENTIALS_400,
        ]),
    }

    refresh_post = {
        status.HTTP_401_UNAUTHORIZED: convert_to_example([
            HTTPError.BAD_CREDENTIALS_401,
            HTTPError.INVALID_TOKEN_401,
            HTTPError.REFRESH_TOKEN_IN_BLACK_LIST_401,
        ]),
        status.HTTP_403_FORBIDDEN: convert_to_example([
            HTTPError.BAD_CREDENTIALS_403,
            HTTPError.DATA_OUT_OF_DATE_403,
            HTTPError.USER_NOT_ACTIVE_403,
        ])
    }