from fastapi import APIRouter, status, Response, Request
from auth.service import UserRepository
from .models import ForgotPassword, ResetPassword
from .responses.http_errors import HTTPError
from .responses.responses import PasswdResponse
from .service import PasswdRepository
from .utils import create_recovery_code
from utils import handle_catch_error


router = APIRouter(prefix="/auth", tags=["Users 👔"])


@router.post(
    path="/forgot_password",
    summary="Request a reset password procedure",
    description="Sends a password recovery code by email",
    response_description="Empty response (status 204)",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses=PasswdResponse.forgot_password_post,
)
@handle_catch_error
async def forgot_password(request: Request, forgot: ForgotPassword):
    user = await UserRepository.find_one_or_none_by_email(str(forgot.email))
    if user is None:
        raise HTTPError.bad_email_400()

    recovery_code = create_recovery_code()

    await request.app.smtp.send_email_code(forgot.email, recovery_code)
    await request.app.redis.add_password_reset_code(forgot.email, recovery_code)

    return Response(status_code=status.HTTP_200_OK)


@router.post(
    path="/reset_password",
    summary="Reset a password",
    description="Reset a password by recovery code in email",
    response_description="Empty response (status 204)",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses=PasswdResponse.reset_password_post,
)
@handle_catch_error
async def reset_password(request: Request, reset: ResetPassword):
    recovery_code = await request.app.redis.get_password_reset_code(reset.email)
    if not recovery_code:
        raise HTTPError.lack_of_email_in_forgotten_400()

    if recovery_code != reset.code:
        raise HTTPError.bad_recovery_code_400()

    check = await PasswdRepository.update_password_by_email(email=str(reset.email), password=reset.password)
    if not check:
        raise HTTPError.bad_email_400()

    await request.app.redis.delete_password_reset_code(reset.email)

    return Response(status_code=status.HTTP_200_OK)