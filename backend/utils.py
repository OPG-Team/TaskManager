from functools import wraps
from typing import Coroutine, Any, Callable, TypeVar
from fastapi import HTTPException, status
from logger import app_logger
from tasks.responses.http_errors import HTTPError as HTTPError_task, TaskErrorCode
from auth.responses.http_errors import HTTPError as HTTPError_auth, UserErrorCode


T = TypeVar('T')


def handle_catch_error(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    """ A decorator for catching errors """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            match (e.status_code, e.detail.get("code")):
                # -------------------- Auth errors --------------------
                case (status.HTTP_400_BAD_REQUEST, UserErrorCode.BAD_CREDENTIALS):
                    raise HTTPError_auth.bad_credentials_400()

                case (status.HTTP_401_UNAUTHORIZED, UserErrorCode.BAD_CREDENTIALS):
                    raise HTTPError_auth.bad_credentials_401()

                case (status.HTTP_401_UNAUTHORIZED, UserErrorCode.INVALID_TOKEN):
                    raise HTTPError_auth.invalid_token_401()

                case (status.HTTP_401_UNAUTHORIZED, UserErrorCode.REFRESH_TOKEN_IN_BLACK_LIST):
                    raise HTTPError_auth.refresh_token_in_black_list_401()

                case (status.HTTP_403_FORBIDDEN, UserErrorCode.BAD_CREDENTIALS):
                    raise HTTPError_auth.bad_credentials_403()

                case (status.HTTP_403_FORBIDDEN, UserErrorCode.NO_ACCESS_RIGHTS):
                    raise HTTPError_auth.no_access_rights_403()

                case (status.HTTP_403_FORBIDDEN, UserErrorCode.USER_NOT_ACTIVE):
                    raise HTTPError_auth.user_not_active_403()

                case (status.HTTP_403_FORBIDDEN, UserErrorCode.DATA_OUT_OF_DATE):
                    raise HTTPError_auth.data_out_of_date_403()

                # -------------------- Task errors --------------------
                case (status.HTTP_400_BAD_REQUEST, TaskErrorCode.USER_ALREADY_ASSOCIATED):
                    raise HTTPError_task.user_already_associated_400()

                case (status.HTTP_400_BAD_REQUEST, TaskErrorCode.OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE):
                    raise HTTPError_task.owner_cannot_change_own_connection_type_400()

                case (status.HTTP_400_BAD_REQUEST, TaskErrorCode.OWNER_CANNOT_DELETE_OWN_CONNECTION):
                    raise HTTPError_task.owner_cannot_delete_own_connection_400()

                # -------------------- Not Found errors --------------------
                case (status.HTTP_404_NOT_FOUND, UserErrorCode.USER_NOT_FOUND):
                    raise HTTPError_auth.user_not_found_404()

                case (status.HTTP_404_NOT_FOUND, TaskErrorCode.TASK_NOT_FOUND):
                    raise HTTPError_task.task_not_found_404()

                case (status.HTTP_404_NOT_FOUND, TaskErrorCode.CONNECTION_NOT_FOUND):
                    raise HTTPError_task.connection_not_found_404()

                case (status.HTTP_409_CONFLICT, UserErrorCode.EMAIL_ALREADY_EXISTS):
                    raise HTTPError_auth.email_already_exists_409()

            raise

        # -------------------- Other error --------------------
        except Exception as e:
            app_logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPError_auth.endpoint_not_found_500()

    return wrapper