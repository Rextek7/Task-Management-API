from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine
from model import Base, User, Task, TaskPermission
from schemas import UserCreate, UserRead, TaskRead, TaskCreate, TaskUpdate, TaskPermissionCreate, Token, \
    TaskPermissionUpdate
from security import get_password_hash, verify_password, create_access_token, get_current_user, get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn
from typing import List

app = FastAPI()
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.

    Проверяет, существует ли пользователь с таким логином. Если существует, выдает ошибку.
    Иначе хеширует пароль и создает нового пользователя в базе данных.
    """

    db_user = db.query(User).filter(User.login == user.login).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(login=user.login, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Авторизация пользователя и выдача токена доступа.

    Проверяет логин и пароль пользователя. Если они верны, создает и возвращает токен доступа.
    """

    user = db.query(User).filter(User.login == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect login or password")
    access_token = create_access_token(data={"sub": user.login})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tasks/", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Создание новой задачи.

    Создает задачу и связывает ее с текущим пользователем.
    """

    db_task = Task(title=task.title, creator_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks/", response_model=List[TaskRead])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    """
    Чтение списка задач.

    Возвращает задачи, созданные текущим пользователем, и задачи, к которым у пользователя есть права на чтение.
    """

    # Список задач, созданных текущим пользователем
    created_tasks = db.query(Task).filter(Task.creator_id == current_user.id)
    # Список задач, к которым текущий пользователь имеет права на чтение
    perm_tasks = db.query(Task).join(TaskPermission).filter(TaskPermission.user_id == current_user.id,
                                                            TaskPermission.can_read == True)
    # Объединение результатов
    tasks = created_tasks.union(perm_tasks).offset(skip).limit(limit).all()

    return tasks


@app.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    """
    Обновление задачи.

    Проверяет права текущего пользователя на обновление задачи и обновляет задачу в базе данных.
    """

    # Проверка прав текущего пользователя
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.creator_id != current_user.id:
        permission = db.query(TaskPermission).filter(TaskPermission.task_id == task_id,
                                                     TaskPermission.user_id == current_user.id,
                                                     TaskPermission.can_update == True).first()
        if not permission:
            raise HTTPException(status_code=403, detail="Not enough permissions to update the task")
    db_task.title = task.title
    db_task.status = task.status
    db.commit()
    db.refresh(db_task)
    return db_task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Удаление задачи.

    Проверяет права текущего пользователя на удаление задачи и удаляет задачу из базы данных.
    """

    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete the task")
    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted"}


@app.post("/tasks/{task_id}/permissions/create/", response_model=TaskPermissionCreate)
def create_task_permission(task_id: int, permission: TaskPermissionCreate, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    """
    Создание прав на задачу.

    Проверяет права текущего пользователя на создание прав и создает новые права для задачи в базе данных.
    """

    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to create")
    db_permission = TaskPermission(task_id=task_id, owner_id=current_user.id, user_id=permission.user_id,
                                   can_read=True if permission.can_update else permission.can_read,
                                   can_update=permission.can_update)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


@app.patch("/tasks/{task_id}/permissions/update/{permission_id}", response_model=TaskPermissionUpdate)
def update_task_permission(task_id: int, permission_id: int, permission: TaskPermissionUpdate,
                           db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Обновление прав на задачу.

    Проверяет права текущего пользователя на обновление прав и обновляет права на задачу в базе данных.
    """

    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_permission = db.query(TaskPermission).filter(TaskPermission.id == permission_id,
                                                    TaskPermission.task_id == task_id).first()
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if db_permission.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to update")
    db_permission.can_read = permission.can_read
    db_permission.can_update = permission.can_update
    db.commit()
    db.refresh(db_permission)
    return db_permission


@app.delete("/tasks/{task_id}/permissions/delete/{permission_id}")
def delete_task_permission(task_id: int, permission_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    """
    Удаление прав на задачу.

    Проверяет права текущего пользователя на удаление прав и удаляет права на задачу из базы данных.
    """

    db_task_permission = db.query(TaskPermission).filter(TaskPermission.id == permission_id,
                                                         TaskPermission.task_id == task_id).first()
    if not db_task_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if db_task_permission.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete")

    db.delete(db_task_permission)
    db.commit()
    return {"detail": "Permission deleted"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
