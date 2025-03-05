from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from auth.models import ConnectionWithUser, UserInfo
from tasks.database import TaskStatus


class TaskCreate(BaseModel):
    title: str
    status: TaskStatus
    description: Optional[str] = None


class TaskBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    time: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskWithUsers(BaseModel):
    id: int
    title: str
    status: TaskStatus
    description: Optional[str]
    time: datetime
    connections: List[ConnectionWithUser]

    model_config = ConfigDict(from_attributes=True)