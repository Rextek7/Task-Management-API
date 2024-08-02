
# Task Management API
## Описание
Этот проект представляет собой API для управления задачами с возможностью регистрации и аутентификации пользователей. Пользователи могут создавать, просматривать, обновлять и удалять задачи, а также выдавать, изменять и отзывать права на чтение и обновление задач другим пользователям.

## Стек технологий
* ### Язык: Python
* ###   Веб-фреймворк: FastAPI
* ###  СУБД: PostgreSQL
* ###   ORM: SQLAlchemy
* ###   Миграции БД: Alembic
* ###   Безопасность: OAuth2 с JWT токенами

## Архитектура
### Проект структурирован следующим образом:


```
project/
├── alembic/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── model.py
│   ├── schemas.py
│   ├── security.py
│   └── database.py
└── tests/
    ├── __init__.py
    ├── test_main.py
    └── conftest.py
    └── tests.py
```
## Подходы и примененные паттерны
* ###  Dependency Injection: Используется для внедрения зависимостей, таких как база данных, в маршруты FastAPI.
* ###   JWT Authentication: Реализована безопасная аутентификация пользователей с использованием JWT токенов.
* ###   Data Transfer Objects (DTOs): Использование Pydantic моделей для валидации данных на входе и выходе.
* ###   Alembic for Migrations: Управление миграциями базы данных с помощью Alembic.

## Модели базы данных

### User:
* #### id: Integer (PK)
* #### login: String (unique)
* #### hashed_password: String
* #### role: String
* #### created_at: DateTime

### Task:
* #### id: Integer (PK)
* #### title: String
* #### status: String (default: "Created")
* #### creator_id: Integer (FK)
* #### created_date: DateTime

### TaskPermission:
* #### id: Integer (PK)
* #### task_id: Integer (FK)
* #### owner_id: Integer (FK)
* #### user_id: Integer (FK)
* #### can_read: Boolean
* #### can_update: Boolean

## Нормализация базы данных
### База данных спроектирована в третьей нормальной форме (3NF):
* #### Первая нормальная форма (1NF): Все столбцы содержат атомарные значения, таблицы не содержат повторяющихся групп.
* #### Вторая нормальная форма (2NF): Все неключевые столбцы зависят от первичного ключа. Таблица Task имеет внешний ключ creator_id, ссылающийся на таблицу User.
* #### Третья нормальная форма (3NF): Все неключевые столбцы не зависят транзитивно от первичного ключа. Таблица TaskPermission содержит только те атрибуты, которые непосредственно относятся к разрешениям задач.


## Тестирование
Для тестирования используются Pytest. Тесты расположены в каталоге tests.

### Примеры запросов
#### Регистрация пользователя

```
POST /register/
{
  "login": "username",
  "password": "password"
  "role": "role"
}
```

#### Создание задачи

```
POST /tasks/
Authorization: Bearer <JWT>
{
  "title": "New Task",
  "status": "Created"
}
```

#### Обновление задачи


```
PATCH /tasks/{task_id}
Authorization: Bearer <JWT>
{
  "title": "Updated Task",
  "status": "In process"
}
```

#### Выдача прав на задачу

```
POST /tasks/{task_id}/permissions/create
Authorization: Bearer <JWT>
{
  "user_id": 2,
  "can_read": true,
  "can_update": false
}
```

#### Обновление прав на задачу

```
PATCH /tasks/{task_id}/permissions/update/{permission_id}
Authorization: Bearer <JWT>
{
  "can_read": true,
  "can_update": true
}
```