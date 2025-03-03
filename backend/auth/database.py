import enum
from sqlalchemy import Enum as SqlEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Model
from tasks.database import TaskOrm


class UserRole(enum.Enum):
    ADMIN = "admin"
    DEFAULT = "default"


class UserOrm(Model):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[SqlEnum[UserRole]] = mapped_column(SqlEnum(UserRole), nullable=False)

    tasks = relationship(argument="TaskOrm", secondary="connection", back_populates="users")


class ConnectionType(enum.Enum):
    OWNER = "Владелец"
    CO_CREATOR = "Соавтор"
    DEFAULT = "Обычный"


class Connection(Model):
    __tablename__ = "connection"

    email: Mapped[str] = mapped_column(ForeignKey("users.email"), primary_key=True)
    id_task: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    type: Mapped[SqlEnum[ConnectionType]] = mapped_column(SqlEnum(ConnectionType), nullable=False)