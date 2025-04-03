from fastapi import status
from auth.responses.http_errors import HTTPError as HTTTPError_auth
from auth.responses.responses import base_auth_responses
from auth.responses.utils import convert_to_example, merge_responses
from tasks.responses.http_errors import HTTPError as HTTTPError_task


class TaskResponses:
    create_new_task = merge_responses(
        base_auth_responses,
        {
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_auth.user_not_found_404(),
            ]),
        }
    )

    update_task = merge_responses(
        base_auth_responses,
        {
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.task_not_found_404(),
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.no_access_rights_403(),
            ]),
        }
    )

    delete_task = merge_responses(
        base_auth_responses,
        {
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.task_not_found_404(),
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.no_access_rights_403(),
            ]),
        }
    )

    add_new_user_on_task = merge_responses(
        base_auth_responses,
        {
            status.HTTP_400_BAD_REQUEST: convert_to_example([
                HTTTPError_task.user_already_associated_400(),
            ]),
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.task_not_found_404(),
                HTTTPError_auth.user_not_found_404(),
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.no_access_rights_403(),
            ]),
        }
    )

    update_connection_type = merge_responses(
        base_auth_responses,
        {
            status.HTTP_400_BAD_REQUEST: convert_to_example([
                HTTTPError_task.owner_cannot_change_own_connection_type_400(),
            ]),
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.task_not_found_404(),
                HTTTPError_task.connection_not_found_404(),
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.no_access_rights_403(),
            ]),
        }
    )

    delete_connection_user = merge_responses(
        base_auth_responses,
        {
            status.HTTP_400_BAD_REQUEST: convert_to_example([
                HTTTPError_task.owner_cannot_delete_own_connection_400(),
            ]),
            status.HTTP_404_NOT_FOUND: convert_to_example([
                HTTTPError_task.task_not_found_404(),
                HTTTPError_task.connection_not_found_404(),
            ]),
            status.HTTP_403_FORBIDDEN: convert_to_example([
                HTTTPError_auth.no_access_rights_403(),
            ]),
        }
    )