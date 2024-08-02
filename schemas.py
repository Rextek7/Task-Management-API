"""
Этот файл содержит определения Pydantic моделей, которые используются для валидации и сериализации данных.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    login: str
    password: str
    role: str

    """
    Модель для создания нового пользователя.

    Атрибуты:
    - login: Логин пользователя.
    - password: Пароль пользователя.
    - role: Роль пользователя.
    """


class UserRead(BaseModel):
    id: int
    login: str
    hashed_password: str

    class Config:
        from_attributes = True

    """
    Модель для чтения информации о пользователе.

    Атрибуты:
    - id: Уникальный идентификатор пользователя.
    - login: Логин пользователя.
    - hashed_password: Хэшированный пароль пользователя.

    Конфигурация:
    - from_attributes: Настройка для работы с атрибутами модели ORM.
    """


class TaskBase(BaseModel):
    title: str
    status: Optional[str] = "Created"

    """
    Базовая модель задачи.

    Атрибуты:
    - title: Название задачи.
    - status: Статус задачи, по умолчанию 'Created'.
    """


class TaskCreate(TaskBase):
    pass

    """
    Модель для создания новой задачи, наследующая атрибуты от TaskBase.
    """


class TaskUpdate(TaskBase):
    pass

    """
    Модель для обновления задачи, наследующая атрибуты от TaskBase.
    """


class TaskRead(TaskBase):
    id: int
    creator_id: int
    creation_date: datetime

    class Config:
        orm_mode = True

    """
    Модель для чтения информации о задаче.

    Атрибуты:
    - id: Уникальный идентификатор задачи.
    - creator_id: Идентификатор пользователя, создавшего задачу.
    - creation_date: Дата и время создания задачи.

    Конфигурация:
    - orm_mode: Настройка для работы с атрибутами модели ORM.
    """


class TaskPermissionCreate(BaseModel):
    user_id: int
    can_read: bool = False
    can_update: bool = False

    """
    Модель для создания прав на задачу.

    Атрибуты:
    - user_id: Идентификатор пользователя, которому назначаются права.
    - can_read: Флаг, разрешающий чтение задачи, по умолчанию False.
    - can_update: Флаг, разрешающий обновление задачи, по умолчанию False.
    """


class TaskPermissionUpdate(BaseModel):
    can_read: bool = False
    can_update: bool = False

    """
    Модель для обновления прав на задачу.

    Атрибуты:
    - can_read: Флаг, разрешающий чтение задачи, по умолчанию False.
    - can_update: Флаг, разрешающий обновление задачи, по умолчанию False.
    """


class Token(BaseModel):
    access_token: str
    token_type: str

    """
    Модель токена доступа.

    Атрибуты:
    - access_token: Токен доступа.
    - token_type: Тип токена.
    """
