"""
Этот файл содержит определения моделей данных, которые представляют таблицы в базе данных.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    Модель пользователя.

    Атрибуты:
    - id: Уникальный идентификатор пользователя.
    - login: Уникальный логин пользователя.
    - hashed_password: Хэшированный пароль пользователя.
    - role: Роль пользователя, по умолчанию 'user'.
    - created: Дата и время создания пользователя.
    """

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default='user')
    created = Column(DateTime, default=datetime.now())


class Task(Base):
    """
    Модель задачи.

    Атрибуты:
    - id: Уникальный идентификатор задачи.
    - title: Название задачи.
    - status: Статус задачи, по умолчанию 'Created'.
    - creator_id: Идентификатор пользователя, создавшего задачу.
    - creation_date: Дата и время создания задачи.
    """

    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    status = Column(String, default="Created")
    creator_id = Column(Integer, ForeignKey('users.id'))
    creation_date = Column(DateTime, default=datetime.now())


class TaskPermission(Base):
    """
    Модель прав доступа к задаче.

    Атрибуты:
    - id: Уникальный идентификатор права доступа.
    - task_id: Идентификатор задачи, к которой относятся права.
    - owner_id: Идентификатор пользователя, владеющего правами доступа.
    - user_id: Идентификатор пользователя, которому назначены права доступа.
    - can_read: Флаг, разрешающий чтение задачи.
    - can_update: Флаг, разрешающий обновление задачи.
    """

    __tablename__ = 'task_permissions'
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    can_read = Column(Boolean, default=False)
    can_update = Column(Boolean, default=False)
