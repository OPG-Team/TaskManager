from fastapi import status
from auth.responses.http_errors import HTTTPError as HTTTPError_auth
from auth.responses.responses import base_auth_responses
from auth.responses.utils import convert_to_example, merge_responses
from tasks.responses.http_errors import HTTTPError as HTTTPError_task


class TaskResponses:
    create_new_task = merge_responses(
        base_auth_responses,
        {
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_auth.USER_NOT_FOUNT_404,
            ]),
        }
    )

    update_task = merge_responses(
        base_auth_responses,
        {
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.TASK_NOT_FOUNT_404,
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.NO_ACCESS_RIGHTS_403,
            ]),
        }
    )

    delete_task = merge_responses(
        base_auth_responses,
        {
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.TASK_NOT_FOUNT_404,
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.NO_ACCESS_RIGHTS_403,
            ]),
        }
    )

    add_new_user_on_task = merge_responses(
        base_auth_responses,
        {
            status.HTTP_400_BAD_REQUEST: convert_to_example([
                HTTTPError_task.USER_ALREADY_ASSOCIATED_400,
            ]),
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.TASK_NOT_FOUNT_404,
                HTTTPError_auth.USER_NOT_FOUNT_404,
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.NO_ACCESS_RIGHTS_403,
            ]),
        }
    )

    update_connection_type = merge_responses(
        base_auth_responses,
        {
            status.HTTP_400_BAD_REQUEST: convert_to_example([
                HTTTPError_task.OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE_400,
            ]),
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.TASK_NOT_FOUNT_404,
                HTTTPError_task.CONNECTION_NOT_FOUND_404,
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.NO_ACCESS_RIGHTS_403,
            ]),
        }
    )

    delete_connection_user = merge_responses(
        base_auth_responses,
        {
            status.HTTP_400_BAD_REQUEST: convert_to_example([
                HTTTPError_task.OWNER_CANNOT_DELETE_OWN_CONNECTION_400,
            ]),
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.TASK_NOT_FOUNT_404,
                HTTTPError_task.CONNECTION_NOT_FOUND_404,
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.NO_ACCESS_RIGHTS_403,
            ]),
        }
    )