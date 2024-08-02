import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from test_main import TestingSessionLocal, init_db, drop_db


# Фикстура для тестового клиента
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# Фикстура для базы данных
@pytest.fixture(scope="function")
def db():
    # Очистка и инициализация базы данных перед каждым тестом
    drop_db()
    init_db()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Подмена зависимости get_db для использования тестовой базы данных
@pytest.fixture(scope="module", autouse=True)
def override_get_db():
    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides[get_db] = get_db
