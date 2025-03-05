from typing import List
from fastapi import APIRouter, status, Response
from fastapi.params import Depends
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
    response_model=TaskWithUsers,
    responses=TaskResponses.create_new_task,
)
async def create_new_task(task: TaskCreate, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.create_new_task(task_data=task, user_email=str(user.email))
    return Response(status_code=status.HTTP_201_CREATED)


@router.put(
    path="/{id}",
    summary="Update a specific task",
    description="Update a specific task",
    response_description="Updated info for task",
    status_code=status.HTTP_200_OK,
    responses=TaskResponses.update_task,
)
async def update_task(id: int, task: TaskCreate, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.update_task(
        task_id=id,
        task_data=task,
        user=user
    )
    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    path="/{id}",
    summary="Delete a specific task",
    description="Delete a specific task",
    response_description="Status code",
    status_code=status.HTTP_200_OK,
    responses=TaskResponses.delete_task,
)
async def delete_task(id: int, user: UserInfo = Depends(get_current_user)):
    await TaskRepository.delete_task(
        task_id=id,
        user=user
    )
    return Response(status_code=status.HTTP_200_OK)
