from typing import List
from fastapi import APIRouter, status, Response
from fastapi.params import Depends
from auth.database import ConnectionType
from auth.dependencies import get_current_user
from auth.models import UserInfo
from auth.responses.responses import base_auth_responses
from tasks.models import TaskWithUsers, TaskCreate
from tasks.responses.responses import TaskResponses
from tasks.service import TaskRepository
from utils import handle_catch_error


router = APIRouter(prefix="/tasks", tags=["Tasks 💡"])


@router.get(
    path="/",
    summary="Get all tasks for current user",
    description="Returns all tasks where current user is owner or participant. Includes task details and user connections. Accessible only to authenticated users.",
    response_description="A list of all tasks in the database",
    status_code=status.HTTP_200_OK,
    response_model=List[TaskWithUsers],
    responses=base_auth_responses,
)
@handle_catch_error
async def get_all_tasks(user: UserInfo = Depends(get_current_user)):
    tasks = await TaskRepository.get_all_tasks_and_users(user)
    return [TaskWithUsers.model_validate(row) for row in tasks]


@router.post(
    path="/",
    summary="Add new task",
    description="Creates task with current user as owner. Requires authentication. Returns 201 on success.",
    response_description="Empty response (status 201)",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
    responses=TaskResponses.create_new_task,
)
@handle_catch_error
async def create_new_task(task: TaskCreate, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.create_new_task(task_data=task, user_email=str(user.email))
    return Response(status_code=status.HTTP_201_CREATED)


@router.put(
    path="/{task_id}",
    summary="Update a specific task",
    description="Modifies task details. Available for owners/co-creators. Validates input data.",
    response_description="Empty response (status 200)",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses=TaskResponses.update_task,
)
@handle_catch_error
async def update_task(task_id: int, task: TaskCreate, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.update_task(
        task_id=task_id,
        task_data=task,
        user=user
    )
    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    path="/{task_id}",
    summary="Delete a specific task",
    description="Permanently removes task. Owner only. Deletes all connections.",
    response_description="Empty response (status 200)",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses=TaskResponses.delete_task,
)
@handle_catch_error
async def delete_task(task_id: int, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.delete_task(
        task_id=task_id,
        user=user
    )
    return Response(status_code=status.HTTP_200_OK)


@router.post(
    path="/add_user/{task_id}",
    summary="Add user on the your task",
    description="Adds user with specified role (owner/co-creator/default). Owner/admin only.",
    response_description="Empty response (status 200)",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses=TaskResponses.add_new_user_on_task,
)
@handle_catch_error
async def add_user_on_task(task_id: int, new_user: str, type_connection: ConnectionType, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.add_user_on_task(
        task_id=task_id,
        new_user_email=new_user,
        type_connection=type_connection,
        user=user
    )
    return Response(status_code=status.HTTP_200_OK)


@router.put(
    path="/update_connection_type/{task_id}",
    summary="Update connection type",
    description="Updates user's connection type. Owner can't demote themselves.",
    response_description="Empty response (status 200)",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses=TaskResponses.update_connection_type,
)
@handle_catch_error
async def update_connection_type_for_user(task_id: int, email_user: str, type_connection: ConnectionType, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.update_connection_type(
        task_id=task_id,
        email_user=email_user,
        type_connection=type_connection,
        current_user=user
    )
    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    path="/delete_connection/{task_id}",
    summary="Delete connection",
    description="Deletes user-task connection. Owner can't remove themselves.",
    response_description="Empty response (status 200)",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses=TaskResponses.delete_connection_user,
)
@handle_catch_error
async def delete_connection_user(task_id: int, email_user: str, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.delete_connection_user(
        task_id=task_id,
        user_email_to_delete=email_user,
        current_user=user
    )
    return Response(status_code=status.HTTP_200_OK)