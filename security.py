"""
Этот файл содержит функции для обработки безопасности, такие как хеширование паролей и создание JWT токенов.
"""
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from model import User

# Конфигурация для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Секретный ключ для подписи JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """
    Проверяет, соответствует ли введенный пароль захешированному паролю.

    Возвращает True, если пароль верен, и False, если нет.
    """

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Хеширует пароль.

    Возвращает захешированный пароль.
    """

    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Создает токен доступа.

    Добавляет в токен время истечения и кодирует его с использованием секретного ключа.
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_db():
    """
    Получает сессию базы данных.

    Открывает сессию базы данных и закрывает ее после использования.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Получает текущего пользователя на основе токена доступа.

    Декодирует токен, извлекает логин пользователя и проверяет, существует ли пользователь в базе данных.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.login == login).first()
    if user is None:
        raise credentials_exception
    return user
