from fastapi import status
from .http_errors import HTTPError
from auth.responses.utils import convert_to_example


class PasswdResponse:
    """res_passwd responses

    Attributes:
        forgot_password_post: Responses for forgot_password_post
        reset_password_post: Responses for reset_password_post
    """
    forgot_password_post = {
        status.HTTP_400_BAD_REQUEST: convert_to_example([
            HTTPError.bad_email_400(),
        ]),
    }

    reset_password_post = {
        status.HTTP_400_BAD_REQUEST: convert_to_example([
            HTTPError.bad_email_400(),
            HTTPError.bad_recovery_code_400(),
            HTTPError.lack_of_email_in_forgotten_400(),
        ]),
    }