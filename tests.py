from sqlalchemy.orm import Session
from model import User, Task
from security import get_password_hash, verify_password, create_access_token
from fastapi.testclient import TestClient
import pytest


def test_register_user_success(client: TestClient, db: Session):
    """
    Проверка на регистрацию пользователя
    """
    response = client.post(
        "/register",
        json={"login": "testuser", "password": "testpassword", "role": "user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["login"] == "testuser"
    assert "id" in data

    db_user = db.query(User).filter(User.login == "testuser").first()
    assert db_user is not None
    assert db_user.login == "testuser"
    assert verify_password("testpassword", db_user.hashed_password)


def test_register_user_already_exists(client: TestClient, db: Session):
    """
    Проверка на уникальность логина и пароля пользователя
    """
    password_hash = get_password_hash("existingpassword")
    db_user = User(login="existinguser", hashed_password=password_hash, role="user")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    response = client.post(
        "/register",
        json={"login": "existinguser", "password": "newpassword", "role": "user"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Login already registered"}


@pytest.fixture
def user_token(db: Session):
    user = User(login="taskuser", hashed_password=get_password_hash("taskpassword"), role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token(data={"sub": user.login})
    return {"Authorization": f"Bearer {access_token}"}


def test_create_task_success(client: TestClient, db: Session, user_token):
    """
    Проверка на возможность создания задания
    """
    response = client.post(
        "/tasks/",
        json={"title": "New Task"},
        headers=user_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Task"
    assert "id" in data

    db_task = db.query(Task).filter(Task.title == "New Task").first()
    assert db_task is not None
    assert db_task.title == "New Task"


def test_read_tasks_success(client: TestClient, db: Session, user_token):
    """
    Проверка на возможность чтения созданных заданий
    """
    user = db.query(User).filter(User.login == "taskuser").first()
    task1 = Task(title="Task 1", creator_id=user.id)
    task2 = Task(title="Task 2", creator_id=user.id)
    db.add(task1)
    db.add(task2)
    db.commit()

    response = client.get("/tasks/", headers=user_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(task["title"] == "Task 1" for task in data)
    assert any(task["title"] == "Task 2" for task in data)
