from .http_errors import HTTPError
from fastapi import status
from .utils import convert_to_example


base_auth_responses = {
    status.HTTP_401_UNAUTHORIZED: convert_to_example([
        HTTPError.bad_credentials_401(),
        HTTPError.invalid_token_401(),
    ]),
    status.HTTP_403_FORBIDDEN: convert_to_example([
        HTTPError.bad_credentials_403(),
        HTTPError.user_not_active_403(),
        HTTPError.data_out_of_date_403(),
    ]),
    status.HTTP_500_INTERNAL_SERVER_ERROR: convert_to_example([
        HTTPError.endpoint_not_found_500(),
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
            HTTPError.email_already_exists_409(),
        ]),
    }

    login_post = {
        status.HTTP_400_BAD_REQUEST: convert_to_example([
            HTTPError.bad_credentials_400(),
        ]),
    }

    refresh_post = {
        status.HTTP_401_UNAUTHORIZED: convert_to_example([
            HTTPError.bad_credentials_401(),
            HTTPError.invalid_token_401(),
            HTTPError.refresh_token_in_black_list_401(),
        ]),
        status.HTTP_403_FORBIDDEN: convert_to_example([
            HTTPError.bad_credentials_403(),
            HTTPError.data_out_of_date_403(),
            HTTPError.user_not_active_403(),
        ])
    }