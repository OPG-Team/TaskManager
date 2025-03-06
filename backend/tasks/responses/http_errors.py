from fastapi import HTTPException, status
from auth.responses.http_errors import ErrorDetail


class TaskErrorCode:
    """Аll tasks error codes.

    Attributes:
        TASK_NOT_FOUND: Task not found.
        USER_ALREADY_ASSOCIATED: User is already associated with this task.
        CONNECTION_NOT_FOUND: No connection found.
        OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE: The OWNER cannot change their own connection type.
    """
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    USER_ALREADY_ASSOCIATED = "USER_ALREADY_ASSOCIATED"
    CONNECTION_NOT_FOUND = "CONNECTION_NOT_FOUND"
    OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE = "OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE"
    OWNER_CANNOT_DELETE_OWN_CONNECTION = "OWNER_CANNOT_DELETE_OWN_CONNECTION"


class HTTTPError:
    """Аll error codes for books.

    Attributes:
        USER_ALREADY_ASSOCIATED_400: User is already associated with this task.
        OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE_400: The OWNER cannot change their own connection type.
        OWNER_CANNOT_DELETE_OWN_CONNECTION_400: The OWNER cannot delete their own connection.
        TASK_NOT_FOUNT_404: Task not found on database.
        CONNECTION_NOT_FOUND_404: No connection found.
    """
    USER_ALREADY_ASSOCIATED_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorDetail(
            code=TaskErrorCode.USER_ALREADY_ASSOCIATED,
            reason="User is already associated with this task"
        ).model_dump(),
    )

    OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorDetail(
            code=TaskErrorCode.OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE,
            reason="The OWNER cannot change their own connection type"
        ).model_dump(),
    )

    OWNER_CANNOT_DELETE_OWN_CONNECTION_400 = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorDetail(
            code=TaskErrorCode.OWNER_CANNOT_DELETE_OWN_CONNECTION,
            reason="The OWNER cannot delete their own connection"
        ).model_dump(),
    )

    TASK_NOT_FOUNT_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorDetail(
            code=TaskErrorCode.TASK_NOT_FOUND,
            reason="Task not found"
        ).model_dump(),
    )

    CONNECTION_NOT_FOUND_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorDetail(
            code=TaskErrorCode.CONNECTION_NOT_FOUND,
            reason="Connection not found"
        ).model_dump(),
    )