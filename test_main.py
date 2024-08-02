"""
Файл с тестами для проверки функциональности API.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base

# Создание тестового движка
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Создание сессии для тестовой базы данных
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для инициализации базы данных
def init_db():
    Base.metadata.create_all(bind=engine)

def drop_db():
    Base.metadata.drop_all(bind=engine)

