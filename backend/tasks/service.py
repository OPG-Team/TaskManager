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
        """Creates a new task in the database and associates it with the user as the owner.

        Args:
            task_data: TaskCreate object with task details (title, status, description).
            user_email: Email of the user creating the task.

        Returns:
            None

        Raises:
            HTTTPError_auth.USER_NOT_FOUNT_404: User not found in the database.
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
            HTTTPError_auth.NO_ACCESS_RIGHTS_403: No required access rights.
            HTTTPError_task.TASK_NOT_FOUNT_404: Task not found on database.
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
            HTTTPError_auth.NO_ACCESS_RIGHTS_403: No required access rights.
            HTTTPError_task.TASK_NOT_FOUNT_404: Task not found on database.
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

    @classmethod
    async def add_user_on_task(cls, task_id: int, new_user_email: str, type_connection: ConnectionType, user: UserInfo) -> TaskWithUsers:
        """Adds a new user to a task with the specified connection type if the current user is the owner or admin.

        Args:
            task_id: ID of the task.
            new_user_email: Email of the user to add to the task.
            type_connection: Connection type for the new user (e.g., CO_CREATOR, DEFAULT).
            user: UserInfo of the current user (the requester).

        Returns:
            The updated TaskWithUsers object with all connections.

        Raises:
            HTTTPError_auth.NO_ACCESS_RIGHTS_403: No required access rights (if DEFAULT user is not OWNER).
            HTTTPError_task.TASK_NOT_FOUNT_404: Task not found in the database.
            HTTTPError_auth.USER_NOT_FOUNT_404: User to add not found in the database.
            HTTTPError_task.USER_ALREADY_ASSOCIATED_400: User is already associated with this task.
        """
        async with new_session() as session:
            # Получаем задачу
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTTPError_task.TASK_NOT_FOUNT_404

            if user.role == UserRole.DEFAULT:
                owner_connection = await session.execute(
                    select(ConnectionOrm).where(
                        ConnectionOrm.id_task == task_id,
                        ConnectionOrm.email == user.email,
                        ConnectionOrm.type == ConnectionType.OWNER
                    )
                )
                if not owner_connection.scalars().first():
                    raise HTTTPError_auth.NO_ACCESS_RIGHTS_403

            new_user = await session.get(UserOrm, new_user_email)
            if not new_user:
                raise HTTTPError_auth.USER_NOT_FOUNT_404

            existing_connection = await session.execute(
                select(ConnectionOrm).where(
                    ConnectionOrm.id_task == task_id,
                    ConnectionOrm.email == new_user_email
                )
            )
            if existing_connection.scalars().first():
                raise HTTTPError_task.USER_ALREADY_ASSOCIATED_400

            new_connection = ConnectionOrm(
                email=new_user_email,
                id_task=task_id,
                type=type_connection
            )
            session.add(new_connection)
            await session.commit()

            result = await session.execute(
                select(TaskOrm)
                .options(joinedload(TaskOrm.users))
                .where(TaskOrm.id == task_id)
            )
            task = result.scalars().first()

            connections_query = await session.execute(
                select(ConnectionOrm).where(ConnectionOrm.id_task == task_id)
            )
            connections = connections_query.scalars().all()

            connection_list = []
            for conn in connections:
                conn_user = next((u for u in task.users if u.email == conn.email), None)
                if conn_user:
                    connection_list.append(
                        ConnectionWithUser(
                            type=conn.type,
                            user=UserInfo.model_validate(conn_user)
                        )
                    )

            task_dict = {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "description": task.description,
                "time": task.time,
                "connections": connection_list
            }
            return TaskWithUsers(**task_dict)

    @classmethod
    async def update_connection_type(cls, task_id: int, email_user: str, type_connection: ConnectionType, current_user: UserInfo) -> TaskWithUsers:
        """Updates the connection type for a user in a task if the current user is the owner.

        Args:
            task_id: ID of the task.
            email_user: Email user for update connection type
            type_connection: Connection type
            current_user: UserInfo of the current user (the requester).

        Returns:
            The updated TaskWithUsers object with all connections.

        Raises:
            HTTTPError_task.OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE_400: The OWNER cannot change their own connection type.
            HTTTPError_auth.NO_ACCESS_RIGHTS_403: No required access rights.
            HTTTPError_task.TASK_NOT_FOUNT_404: Task not found on database.
            HTTTPError_task.CONNECTION_NOT_FOUND_404: No connection found.
        """
        async with new_session() as session:
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTTPError_task.TASK_NOT_FOUNT_404

            if current_user.role == UserRole.DEFAULT:
                owner_connection = await session.execute(
                    select(ConnectionOrm).where(
                        ConnectionOrm.id_task == task_id,
                        ConnectionOrm.email == current_user.email,
                        ConnectionOrm.type == ConnectionType.OWNER
                    )
                )
                if not owner_connection.scalars().first():
                    raise HTTTPError_auth.NO_ACCESS_RIGHTS_403

            connection = await session.execute(
                select(ConnectionOrm).where(
                    ConnectionOrm.id_task == task_id,
                    ConnectionOrm.email == email_user
                )
            )
            connection = connection.scalars().first()
            if not connection:
                raise HTTTPError_task.CONNECTION_NOT_FOUND_404

            # Проверяем, не пытается ли владелец изменить свой собственный тип связи
            if connection.email == current_user.email and type_connection != ConnectionType.OWNER:
                raise HTTTPError_task.OWNER_CANNOT_CHANGE_OWN_CONNECTION_TYPE_400

            # Обновляем тип связи
            connection.type = type_connection
            await session.commit()

            # Загружаем обновлённую задачу с пользователями
            result = await session.execute(
                select(TaskOrm)
                .options(joinedload(TaskOrm.users))
                .where(TaskOrm.id == task_id)
            )
            task = result.scalars().first()

            # Получаем все связи для задачи
            connections_query = await session.execute(
                select(ConnectionOrm).where(ConnectionOrm.id_task == task_id)
            )
            connections = connections_query.scalars().all()

            # Формируем список связей
            connection_list = []
            for conn in connections:
                conn_user = next((u for u in task.users if u.email == conn.email), None)
                if conn_user:
                    connection_list.append(
                        ConnectionWithUser(
                            type=conn.type,
                            user=UserInfo.model_validate(conn_user)
                        )
                    )

            task_dict = {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "description": task.description,
                "time": task.time,
                "connections": connection_list
            }
            return TaskWithUsers(**task_dict)

    @classmethod
    async def delete_connection_user(cls, task_id: int, user_email_to_delete: str, current_user: UserInfo) -> TaskWithUsers:
        """Deletes a user's connection to a task if the current user is the owner.

        Args:
            task_id: ID of the task.
            user_email_to_delete: Email of the user whose connection to delete.
            current_user: UserInfo of the current user (the requester).

        Returns:
            The updated TaskWithUsers object with remaining connections.

        Raises:
            HTTTPError_task.OWNER_CANNOT_DELETE_OWN_CONNECTION_400: The OWNER cannot delete their own connection.
            HTTTPError_auth.NO_ACCESS_RIGHTS_403: No required access rights.
            HTTTPError_task.TASK_NOT_FOUNT_404: Task not found on database.
            HTTTPError_task.CONNECTION_NOT_FOUND_404: No connection found.
        """
        async with new_session() as session:
            # Получаем задачу
            task = await session.get(TaskOrm, task_id)
            if not task:
                raise HTTTPError_task.TASK_NOT_FOUNT_404

            # Проверяем, является ли текущий пользователь владельцем
            if current_user.role == UserRole.DEFAULT:
                owner_connection = await session.execute(
                    select(ConnectionOrm).where(
                        ConnectionOrm.id_task == task_id,
                        ConnectionOrm.email == current_user.email,
                        ConnectionOrm.type == ConnectionType.OWNER
                    )
                )
                if not owner_connection.scalars().first():
                    raise HTTTPError_auth.NO_ACCESS_RIGHTS_403

            # Проверяем, не пытается ли владелец удалить свою связь
            if user_email_to_delete == current_user.email:
                raise HTTTPError_task.OWNER_CANNOT_DELETE_OWN_CONNECTION_400

            # Проверяем существование связи для удаления
            connection_to_delete = await session.execute(
                select(ConnectionOrm).where(
                    ConnectionOrm.id_task == task_id,
                    ConnectionOrm.email == user_email_to_delete
                )
            )
            connection = connection_to_delete.scalars().first()
            if not connection:
                raise HTTTPError_task.CONNECTION_NOT_FOUND_404

            # Удаляем связь
            await session.delete(connection)
            await session.commit()

            # Загружаем обновлённую задачу с пользователями
            result = await session.execute(
                select(TaskOrm)
                .options(joinedload(TaskOrm.users))
                .where(TaskOrm.id == task_id)
            )
            task = result.scalars().first()

            # Получаем оставшиеся связи для задачи
            connections_query = await session.execute(
                select(ConnectionOrm).where(ConnectionOrm.id_task == task_id)
            )
            connections = connections_query.scalars().all()

            # Формируем список связей
            connection_list = []
            for conn in connections:
                conn_user = next((u for u in task.users if u.email == conn.email), None)
                if conn_user:
                    connection_list.append(
                        ConnectionWithUser(
                            type=conn.type,
                            user=UserInfo.model_validate(conn_user)
                        )
                    )

            task_dict = {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "description": task.description,
                "time": task.time,
                "connections": connection_list
            }
            return TaskWithUsers(**task_dict)