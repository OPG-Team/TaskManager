import enum
from datetime import datetime
from sqlalchemy import Enum as SqlEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Model


class TaskStatus(enum.Enum):
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    COMPLETED = "Завершена"


class TaskOrm(Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[SqlEnum[TaskStatus]] = mapped_column(SqlEnum(TaskStatus), nullable=False)
    description: Mapped[str]
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    users = relationship(argument="UserOrm", secondary="connection", back_populates="tasks")
