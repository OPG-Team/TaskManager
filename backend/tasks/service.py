import datetime
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from auth.database import UserOrm, ConnectionOrm, ConnectionType, UserRole
from auth.models import UserInfo, ConnectionWithUser
from database import new_session
from tasks.database import TaskOrm
from tasks.models import TaskCreate, TaskWithUsers
from tasks.responses.http_errors import HTTTPError as HTTTPError_task
from auth.responses.http_errors import HTTTPError as HTTTPError_auth


class TaskRepository:
    @classmethod
    async def get_all_tasks_and_users(cls, user: UserInfo) -> List[TaskWithUsers]:
        """Retrieves all tasks from the database with their associated users and connection types.

        Returns:
            A List[TaskWithUsers], list of all task objects with their connections.
        """
        async with new_session() as session:
            # Загружаем задачи с пользователями
            query = (
                select(TaskOrm)
                .join(ConnectionOrm, ConnectionOrm.id_task == TaskOrm.id)
                .where(ConnectionOrm.email == user.email)  # Фильтр по email пользователя
                .options(joinedload(TaskOrm.users))  # Загружаем связанных пользователей
            )
            result = await session.execute(query)
            task_models = result.unique().scalars().all()

            # Собираем данные о связях
            tasks_with_connections = []
            for task in task_models:
                # Получаем все связи для данной задачи
                connections_query = await session.execute(
                    select(ConnectionOrm).where(ConnectionOrm.id_task == task.id)
                )
                connections = connections_query.scalars().all()

                # Формируем список связей с пользователями
                connection_list = []
                for conn in connections:
                    user = next((u for u in task.users if u.email == conn.email), None)
                    if user:
                        connection_list.append(
                            ConnectionWithUser(
                                type=conn.type,
                                user=UserInfo.model_validate(user)
                            )
                        )

                # Создаём Pydantic-модель для задачи
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "description": task.description,
                    "time": task.time,
                    "connections": connection_list
                }
                tasks_with_connections.append(TaskWithUsers(**task_dict))

            return tasks_with_connections

    @classmethod
    async def create_new_task(cls, task_data: TaskCreate, user_email: str) -> None:
        async with new_session() as session:
            new_task = TaskOrm(
                title=task_data.title,
                status=task_data.status,
                description=task_data.description,
                time=datetime.datetime.now()
            )
            session.add(new_task)
            await session.flush()

            user = await session.get(UserOrm, user_email)
            if not user:
                raise HTTTPError_auth.USER_NOT_FOUNT_404

            connection = ConnectionOrm(
                email=user_email,
                id_task=new_task.id,
                type=ConnectionType.OWNER
            )
            session.add(connection)

            await session.commit()

    @classmethod
    async def update_task(cls, task_id: int, task_data: TaskCreate, user: UserInfo) -> None:
        """Updates a task in the database if the user has permission.

        Args:
            task_id: ID of the task to update.
            task_data: TaskUpdate object with fields to update.
            user: UserInfo object

        Returns:
            The updated TaskOrm object.

        Raises:
            HTTPException: If the task is not found or the user lacks permission.
        """
        async with new_session() as session:
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTTPError_task.TASK_NOT_FOUNT_404

            if user.role == UserRole.DEFAULT:
                # Проверяем тип связи для пользователя с ролью DEFAULT
                connection = await session.execute(
                    select(ConnectionOrm).where(
                        ConnectionOrm.id_task == task_id,
                        ConnectionOrm.email == user.email
                    )
                )
                connection = connection.scalars().first()
                # Разрешаем обновление только если тип связи OWNER или CO_CREATOR
                if not connection or connection.type not in [ConnectionType.OWNER, ConnectionType.CO_CREATOR]:
                    raise HTTTPError_auth.NO_ACCESS_RIGHTS_403

            # Обновляем поля задачи
            for field, value in task_data.model_dump(exclude_unset=True).items():
                setattr(task, field, value)

            await session.commit()

    @classmethod
    async def delete_task(cls, task_id: int, user: UserInfo) -> None:
        """Updates a task in the database if the user has permission.

        Args:
            task_id: ID of the task to delete.
            user: UserInfo object

        Raises:
            HTTPException: If the task is not found or the user lacks permission.
        """
        async with new_session() as session:
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTTPError_task.TASK_NOT_FOUNT_404

            if user.role == UserRole.DEFAULT:
                connection = await session.execute(
                    select(ConnectionOrm).where(
                        ConnectionOrm.id_task == task_id,
                        ConnectionOrm.email == user.email
                    )
                )
                connection = connection.scalars().first()
                if not connection or connection.type != ConnectionType.OWNER:
                    raise HTTTPError_auth.NO_ACCESS_RIGHTS_403

            await session.delete(task)
            await session.commit()