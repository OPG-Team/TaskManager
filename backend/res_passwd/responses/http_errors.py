from fastapi import HTTPException, status
from auth.responses.http_errors import ErrorDetail


class PasswdErrorCode:
    """Аll res_passwd error codes.

    Attributes:
        BAD_EMAIL: Bad email
        LACK_OF_EMAIL_IN_FORGOTTEN:
        BAD_RECOVERY_CODE:
    """
    BAD_EMAIL = "BAD_EMAIL"
    LACK_OF_EMAIL_IN_FORGOTTEN = "LACK_OF_EMAIL_IN_FORGOTTEN"
    BAD_RECOVERY_CODE = "BAD_RECOVERY_CODE"


class HTTPError:
    """Аll res_passwd errors.

    Methods:
        bad_email_400: Bad email
        lack_of_email_in_forgotten_400: Lack of email on the forgotten list
        bad_recovery_code_400: Bad recovery code for input email
    """
    @staticmethod
    def bad_email_400():
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                code=PasswdErrorCode.BAD_EMAIL,
                reason="Non-existent email in the application"
            ).model_dump(),
        )

    @staticmethod
    def lack_of_email_in_forgotten_400():
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                code=PasswdErrorCode.LACK_OF_EMAIL_IN_FORGOTTEN,
                reason="Lack of email on the forgotten list"
            ).model_dump(),
        )

    @staticmethod
    def bad_recovery_code_400():
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                code=PasswdErrorCode.BAD_RECOVERY_CODE,
                reason="Bad recovery code for input email"
            ).model_dump(),
        )