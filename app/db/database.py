from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL для подключения к базе данных
# DATABASE_URL = "postgresql://postgres:1234@db:5432/microblog"
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/microblog"

# Создание подключения к базе данных
engine = create_engine(DATABASE_URL)

# Определение базового класса для моделей
Base = declarative_base()

# Создание фабрики сессий для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Генератор для получения сессии базы данных.

    Возвращает:
    - db: сессия базы данных (SessionLocal), которая будет
    автоматически закрыта после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
