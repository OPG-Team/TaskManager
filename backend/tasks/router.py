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


router = APIRouter(prefix="/tasks", tags=["Tasks 💡"])


@router.get(
    path="/",
    summary="Get all tasks",
    description="Get all tasks",
    response_description="A list of all tasks in the database",
    status_code=status.HTTP_200_OK,
    response_model=List[TaskWithUsers],
    responses=base_auth_responses,
)
async def get_all_tasks(user: UserInfo = Depends(get_current_user)):
    tasks = await TaskRepository.get_all_tasks_and_users(user)
    return [TaskWithUsers.model_validate(row) for row in tasks]


@router.post(
    path="/",
    summary="Add new task",
    description="Add new task",
    response_description="The task object from the database",
    status_code=status.HTTP_201_CREATED,
    responses=TaskResponses.create_new_task,
)
async def create_new_task(task: TaskCreate, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.create_new_task(task_data=task, user_email=str(user.email))
    return Response(status_code=status.HTTP_201_CREATED)


@router.put(
    path="/{task_id}",
    summary="Update a specific task",
    description="Update a specific task",
    response_description="Updated info for task",
    status_code=status.HTTP_200_OK,
    responses=TaskResponses.update_task,
)
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
    description="Delete a specific task",
    response_description="Status code",
    status_code=status.HTTP_200_OK,
    responses=TaskResponses.delete_task,
)
async def delete_task(task_id: int, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.delete_task(
        task_id=task_id,
        user=user
    )
    return Response(status_code=status.HTTP_200_OK)


@router.post(
    path="/add_user/{task_id}",
    summary="Add user on the your task",
    description="Add user on the your task",
    response_description="TaskWithUsers",
    status_code=status.HTTP_200_OK,
    responses=TaskResponses.add_new_user_on_task,
)
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
    description="Update connection type",
    response_description="TaskWithUsers",
    status_code=status.HTTP_200_OK,
    responses=TaskResponses.update_connection_type,
)
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
    description="Delete connection",
    response_description="TaskWithUsers",
    status_code=status.HTTP_200_OK,
    responses=TaskResponses.delete_connection_user,
)
async def delete_connection_user(task_id: int, email_user: str, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.delete_connection_user(
        task_id=task_id,
        user_email_to_delete=email_user,
        current_user=user
    )
    return Response(status_code=status.HTTP_200_OK)