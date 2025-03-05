from fastapi import HTTPException, status
from auth.responses.http_errors import ErrorDetail


class TaskErrorCode:
    """Аll tasks error codes.

    Attributes:
        TASK_NOT_FOUND: Task not found.
    """
    TASK_NOT_FOUND = "TASK_NOT_FOUND"

class HTTTPError:
    """Аll error codes for books.

    Attributes:
        TASK_NOT_FOUNT_404: Task not found on database.
    """
    TASK_NOT_FOUNT_404 = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorDetail(
            code=TaskErrorCode.TASK_NOT_FOUND,
            reason="Task not found"
        ).model_dump(),
    )
