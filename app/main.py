# import asyncpg
import os
from contextlib import asynccontextmanager

import asyncpg
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api import media, tweets, users

# from alembic.config import Config
# from alembic import command
from app.db import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения.

    Эта функция выполняет начальную настройку базы данных и запуск миграций,
    а также гарантирует, что соединение с базой данных будет
    закрыто при завершении работы приложения.

    Аргументы:
    - app: FastAPI приложение, которому будет предоставлен доступ
    для управления жизненным циклом.

    Возвращаемое значение:
    - None. Функция используется как контекстный менеджер,
    который предоставляет управление приложением.
    """
    print("Starting up...")
    # await create_database_if_not_exists()

    # # Автоматический запуск миграций
    # alembic_cfg = Config("alembic.ini")
    # print("Running Alembic migrations...")
    # command.upgrade(alembic_cfg, "head")
    # print("Running Alembic migrations...   ")
    # Возвращаем управление приложению
    yield

    # Событие завершения работы
    print("Shutting down database connection...")
    if database.SessionLocal:
        session = database.SessionLocal()
        session.close()


app = FastAPI(
    title="My API",
    max_upload_size=10485760,
    description="This is a sample API",
    version="1.0.0",
    openapi_tags=[
        {"name": "users", "description": "Operations with users"},
        {"name": "tweets", "description": "Operations with tweets"},
        {"name": "media", "description": "Operations with media"},
    ],
    lifespan=lifespan,
)
"""
FastAPI приложение, которое настраивает маршруты и
среду для работы с пользователями, твитами и медиа.
"""


app.mount(
    "/css",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../css")),
    name="css",
)
app.mount(
    "/js",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../js")),
    name="js",
)
app.mount("/media", StaticFiles(directory="app/media"), name="media")
"""
Маршруты для обслуживания статических файлов CSS, JS и медиа.
Эти маршруты позволяют серверу отдавать статические ресурсы.
"""


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""
Добавление CORS middleware, чтобы разрешить доступ к API с любых источников.
"""
app.include_router(tweets.router)
app.include_router(users.router)
app.include_router(media.router)
"""
Включение маршрутов для работы с твитами, пользователями и медиа.
Эти маршруты будут обрабатывать соответствующие API запросы.
"""
# DATABASE_URL = "postgresql://postgres:1234@db:5432/microblog"
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/microblog"

"""
Конфигурация URL для подключения к базе данных PostgreSQL.
"""


async def create_database_if_not_exists():
    """
    Создание базы данных, если она не существует. Эта функция
    подключается к серверу PostgreSQL
    и создает базу данных, если она еще не была создана.

    Возвращаемое значение:
    - None
    """
    connection = await asyncpg.connect(
        user="postgres", password="1234", database="microblog", host="db"
    )
    try:
        await connection.execute(f"CREATE DATABASE {DATABASE_URL.split('/')[-1]}")
    except asyncpg.exceptions.DuplicateDatabaseError:
        print("Database already exists.")
    finally:
        await connection.close()


@app.get("/", response_class=HTMLResponse)
async def read_index():
    """
    Главная страница, которая возвращает HTML содержимое.
    Используется для отображения домашней страницы приложения.

    Возвращаемое значение:
    - HTMLResponse: HTML содержимое домашней страницы.
    """
    with open("app/index.html") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    """
    Запуск приложения на сервере Uvicorn с логированием уровня info на порту 8000.

    Возвращаемое значение:
    - None. Эта функция запускает сервер FastAPI.
    """
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")

    

