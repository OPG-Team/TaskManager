import datetime
import locale
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from auth.database import UserOrm, ConnectionOrm, ConnectionType, UserRole
from auth.models import UserInfo, ConnectionWithUser
from database import new_session
from logger import app_logger
from tasks.database import TaskOrm
from tasks.models import TaskCreate, TaskWithUsers
from tasks.responses.http_errors import HTTPError as HTTPError_task
from auth.responses.http_errors import HTTPError as HTTPError_auth


for loc in ['ru_RU.UTF-8', 'ru_RU.utf8', 'Russian', '']:
    try:
        locale.setlocale(locale.LC_TIME, loc)
        app_logger.info(f"Locale setting: {loc}")
        break
    except locale.Error:
        continue


class TaskRepository:
    @classmethod
    async def get_connect_by_task_id_and_email(cls, email_user: str, task_id: int, session: AsyncSession) -> Optional[ConnectionOrm]:
        """Retrieves a connection between task and user from the database.

        Args:
            email_user: Email of the user to find connection for.
            task_id: ID of the task to find connection for.
            session: AsyncSession for database operations.

        Returns:
            A Optional[ConnectionOrm], the found connection object or None if not exists.
        """
        connection = await session.execute(
            select(ConnectionOrm).where(
                ConnectionOrm.id_task == task_id,
                ConnectionOrm.email == email_user
            )
        )
        return connection.scalars().first()

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
                .where(ConnectionOrm.email == user.email)
                .options(selectinload(TaskOrm.users))  # Загружаем связанных пользователей
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
                task_dict = task.__dict__.copy()
                task_dict["connections"] = connection_list
                tasks_with_connections.append(TaskWithUsers.model_validate(task_dict))

            return tasks_with_connections

    @classmethod
    async def create_new_task(cls, task_data: TaskCreate, user_email: str) -> None:
        """Creates a new task in the database and associates it with the user as the owner.

        Args:
            task_data: TaskCreate object with task details (title, status, description).
            user_email: Email of the user creating the task.

        Returns:
            None

        Raises:
            HTTTPError_auth.user_not_found_404(): User not found in the database.
        """
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
                raise HTTPError_auth.user_not_found_404()

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
            HTTTPError_auth.no_access_rights_403(): No required access rights.
            HTTTPError_task.task_not_found_404(): Task not found on database.
        """
        async with new_session() as session:
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTPError_task.task_not_found_404()

            if user.role == UserRole.DEFAULT:
                connection = await cls.get_connect_by_task_id_and_email(email_user=str(user.email), task_id=task_id, session=session)
                if not connection or connection.type not in [ConnectionType.OWNER, ConnectionType.CO_CREATOR]:
                    raise HTTPError_auth.no_access_rights_403()

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

        Returns:
            None

        Raises:
            HTTTPError_auth.no_access_rights_403(): No required access rights.
            HTTTPError_task.task_not_found_404(): Task not found on database.
        """
        async with new_session() as session:
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTPError_task.task_not_found_404()

            if user.role == UserRole.DEFAULT:
                connection = await cls.get_connect_by_task_id_and_email(email_user=str(user.email), task_id=task_id, session=session)
                if not connection or connection.type not in [ConnectionType.OWNER]:
                    raise HTTPError_auth.no_access_rights_403()

            await session.delete(task)
            await session.commit()

    @classmethod
    async def add_user_on_task(cls, task_id: int, new_user_email: str, type_connection: ConnectionType, user: UserInfo) -> None:
        """Adds a new user to a task with the specified connection type if the current user is the owner or admin.

        Args:
            task_id: ID of the task.
            new_user_email: Email of the user to add to the task.
            type_connection: Connection type for the new user (e.g., CO_CREATOR, DEFAULT).
            user: UserInfo of the current user (the requester).

        Returns:
            None

        Raises:
            HTTTPError_auth.no_access_rights_403(): No required access rights (if DEFAULT user is not OWNER).
            HTTTPError_task.task_not_found_404(): Task not found in the database.
            HTTTPError_auth.user_not_found_404(): User to add not found in the database.
            HTTTPError_task.user_already_associated_400(): User is already associated with this task.
        """
        async with new_session() as session:
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTPError_task.task_not_found_404()

            if user.role == UserRole.DEFAULT:
                connection = await cls.get_connect_by_task_id_and_email(email_user=str(user.email), task_id=task_id, session=session)
                if not connection or connection.type not in [ConnectionType.OWNER]:
                    raise HTTPError_auth.no_access_rights_403()

            new_user = await session.get(UserOrm, new_user_email)
            if not new_user:
                raise HTTPError_auth.user_not_found_404()

            existing_connection = await cls.get_connect_by_task_id_and_email(email_user=new_user_email, task_id=task_id, session=session)
            if existing_connection:
                raise HTTPError_task.user_already_associated_400()

            new_connection = ConnectionOrm(
                email=new_user_email,
                id_task=task_id,
                type=type_connection
            )
            session.add(new_connection)
            await session.commit()

    @classmethod
    async def update_connection_type(cls, task_id: int, email_user: str, type_connection: ConnectionType, current_user: UserInfo) -> None:
        """Updates the connection type for a user in a task if the current user is the owner.

        Args:
            task_id: ID of the task.
            email_user: Email user for update connection type
            type_connection: Connection type
            current_user: UserInfo of the current user (the requester).

        Returns:
            None

        Raises:
            HTTTPError_task.owner_cannot_change_own_connection_type_400(): The OWNER cannot change their own connection type.
            HTTTPError_auth.no_access_rights_403(): No required access rights.
            HTTTPError_task.task_not_found_404(): Task not found on database.
            HTTTPError_task.connection_not_found_404(): No connection found.
        """
        async with new_session() as session:
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTPError_task.task_not_found_404()

            if current_user.role == UserRole.DEFAULT:
                connection = await cls.get_connect_by_task_id_and_email(email_user=str(current_user.email), task_id=task_id, session=session)
                if not connection or connection.type not in [ConnectionType.OWNER]:
                    raise HTTPError_auth.no_access_rights_403()

            connection = await cls.get_connect_by_task_id_and_email(email_user=email_user, task_id=task_id, session=session)
            if not connection:
                raise HTTPError_task.connection_not_found_404()

            # Проверяем, не пытается ли владелец изменить свой собственный тип связи
            if connection.email == current_user.email and type_connection != ConnectionType.OWNER:
                raise HTTPError_task.owner_cannot_change_own_connection_type_400()

            # Обновляем тип связи
            connection.type = type_connection
            await session.commit()


    @classmethod
    async def delete_connection_user(cls, task_id: int, user_email_to_delete: str, current_user: UserInfo) -> None:
        """Deletes a user's connection to a task if the current user is the owner.

        Args:
            task_id: ID of the task.
            user_email_to_delete: Email of the user whose connection to delete.
            current_user: UserInfo of the current user (the requester).

        Returns:
            None

        Raises:
            HTTTPError_task.owner_cannot_delete_own_connection_400(): The OWNER cannot delete their own connection.
            HTTTPError_auth.no_access_rights_403(): No required access rights.
            HTTTPError_task.task_not_found_404(): Task not found on database.
            HTTTPError_task.connection_not_found_404(): No connection found.
        """
        async with new_session() as session:
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTPError_task.task_not_found_404()

            if current_user.role == UserRole.DEFAULT:
                connection = await cls.get_connect_by_task_id_and_email(email_user=str(current_user.email), task_id=task_id, session=session)
                if not connection or connection.type not in [ConnectionType.OWNER]:
                    raise HTTPError_auth.no_access_rights_403()

            # Проверяем, не пытается ли владелец удалить свою связь
            if user_email_to_delete == current_user.email:
                raise HTTPError_task.owner_cannot_delete_own_connection_400()

            # Проверяем существование связи для удаления
            connection = await cls.get_connect_by_task_id_and_email(email_user=user_email_to_delete, task_id=task_id, session=session)
            if not connection:
                raise HTTPError_task.connection_not_found_404()

            # Удаляем связь
            await session.delete(connection)
            await session.commit()