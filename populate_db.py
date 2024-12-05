# populate_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import Tweet, User, UserFollower

# DATABASE_URL = "postgresql://postgres:1234@db:5432/microblog"
DATABASE_URL = "postgresql://postgres:1234@localhost:5432/microblog"


# Создание подключения к базе данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
db = SessionLocal()


def populate_database():
    """
    Функция для заполнения базы данных тестовыми данными:
    - Создается три пользователя с уникальными API ключами, если
    они не существуют в базе данных.
    - Для каждого пользователя создаются три тестовых твита.
    - Пользователи становятся подписчиками друг друга.

    Возвращаемое значение:
    - None
    """
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    # Создание пользователей с уникальными API ключами, если они не существуют
    users_data = [
        {"name": "Test User 1", "api_key": "test"},
        {"name": "Test User 2", "api_key": "test1"},
        {"name": "Test User 3", "api_key": "test2"},
    ]
    for user_data in users_data:
        user = db.query(User).filter(User.api_key == user_data["api_key"]).first()
        if not user:
            user = User(name=user_data["name"], api_key=user_data["api_key"])
            db.add(user)
            db.commit()
            db.refresh(user)

        # Создаем 3 тестовых твита для каждого пользователя
        for i in range(3):
            tweet = Tweet(
                content=f"Это тестовый твит #{i + 1} от {user.name}", user_id=user.id
            )
            db.add(tweet)

    # Создание подписок между пользователями
    user_1 = db.query(User).filter(User.api_key == "test").first()
    user_2 = db.query(User).filter(User.api_key == "test1").first()
    user_3 = db.query(User).filter(User.api_key == "test2").first()

    if user_1 and user_2:
        follower_relationship_1 = UserFollower(
            follower_id=user_1.id, following_id=user_2.id
        )
        follower_relationship_2 = UserFollower(
            follower_id=user_2.id, following_id=user_1.id
        )
        db.add(follower_relationship_1)
        db.add(follower_relationship_2)

    if user_2 and user_3:
        follower_relationship_3 = UserFollower(
            follower_id=user_2.id, following_id=user_3.id
        )
        follower_relationship_4 = UserFollower(
            follower_id=user_3.id, following_id=user_2.id
        )
        db.add(follower_relationship_3)
        db.add(follower_relationship_4)

    if user_3 and user_1:
        follower_relationship_5 = UserFollower(
            follower_id=user_3.id, following_id=user_1.id
        )
        follower_relationship_6 = UserFollower(
            follower_id=user_1.id, following_id=user_3.id
        )
        db.add(follower_relationship_5)
        db.add(follower_relationship_6)

    db.commit()
    db.close()
    print("Тестовые данные введены!")


if __name__ == "__main__":
    populate_database()
