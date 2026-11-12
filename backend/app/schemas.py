from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# --- Схемы для чтения справочников ---
class RoleResponse(BaseModel):
    id: int
    name: str
    class Config: from_attributes = True

class StatusResponse(BaseModel):
    id: int
    name: str
    class Config: from_attributes = True

class PriorityResponse(BaseModel):
    id: int
    name: str
    sla_hours: int
    class Config: from_attributes = True

# --- Пользователи ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str # В реальности тут будет хэш, но для MVP сойдет
    role_id: int

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: RoleResponse
    created_at: datetime
    class Config: from_attributes = True

# --- Заявки ---
class TicketCreate(BaseModel):
    title: str
    description: str
    author_id: int
    priority_id: int = 2 # 2 = Medium по умолчанию

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: StatusResponse
    priority: PriorityResponse
    author_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    class Config: from_attributes = True

class TicketUpdate(BaseModel):
    status_id: Optional[int] = None
    assignee_id: Optional[int] = None

# --- Комментарии ---
class CommentCreate(BaseModel):
    author_id: int
    text: str

class CommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    text: str
    created_at: datetime
    class Config: from_attributes = True