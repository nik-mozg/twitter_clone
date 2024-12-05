from typing import Dict, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import models


async def get_user_by_api_key(api_key: str, db: Session) -> Optional[models.User]:
    """
    Получает пользователя по API ключу, расшифровывая его с использованием
    pgp_sym_decrypt в SQL.

    Args:
        api_key (str): API ключ для поиска пользователя.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        Optional[models.User]: Пользователь, если найден, иначе None.
    """
    sql_query = text(
        """
        SELECT id, name
        FROM users
        WHERE pgp_sym_decrypt(api_key::bytea, :secret_key) = :api_key
        LIMIT 1
    """
    )

    # Выполнение запроса с параметрами
    result = db.execute(
        sql_query, {"secret_key": "your-secret-key", "api_key": api_key}
    ).fetchone()

    # Возвращаем пользователя, если найден
    if result:
        user = models.User(id=result.id, name=result.name)
        return user
    return None


async def get_user_info(user_id: int, db: Session) -> Optional[Dict]:
    """
    Получает информацию о пользователе, включая его подписчиков и тех,
    на кого он подписан.

    Эта функция выполняет запрос к базе данных, чтобы получить информацию
    о пользователе с указанным ID,
    а также его подписчиков и тех, на кого он подписан.

    Args:
        user_id (int): Идентификатор пользователя для получения информации.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        Optional[Dict]: Словарь с информацией о пользователе, включая его
        подписчиков и подписок, если пользователь найден.
        Возвращает None, если пользователь не найден.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        print(f"No user found with user_id: {user_id}")
        return None

    followers = (
        db.query(models.UserFollower)
        .filter(models.UserFollower.following_id == user_id)
        .all()
    )
    following = (
        db.query(models.UserFollower)
        .filter(models.UserFollower.follower_id == user_id)
        .all()
    )

    followers_info = [
        {"id": follower.follower.id, "name": follower.follower.name}
        for follower in followers
    ]
    following_info = [
        {"id": follow.following.id, "name": follow.following.name}
        for follow in following
    ]

    user_info = {
        "id": user.id,
        "name": user.name,
        "followers": followers_info,
        "following": following_info,
    }
    return user_info


async def follow_user(follower_id: int, following_id: int, db: Session) -> None:
    """
    Подписывается на пользователя.

    Эта функция создает новую запись о подписке пользователя на другого пользователя.

    Args:
        follower_id (int): Идентификатор пользователя, который подписывается.
        following_id (int): Идентификатор пользователя, на которого подписываются.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        None
    """
    new_follow = models.UserFollower(follower_id=follower_id, following_id=following_id)
    db.add(new_follow)
    db.commit()


async def unfollow_user(follower_id: int, following_id: int, db: Session) -> None:
    """
    Отписывается от пользователя.

    Эта функция удаляет запись о подписке пользователя на другого пользователя.

    Args:
        follower_id (int): Идентификатор пользователя, который отписывается.
        following_id (int): Идентификатор пользователя, от которого отписываются.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        None
    """
    follow_relation = (
        db.query(models.UserFollower)
        .filter(
            models.UserFollower.follower_id == follower_id,
            models.UserFollower.following_id == following_id,
        )
        .first()
    )

    if follow_relation:
        db.delete(follow_relation)
        db.commit()


async def get_user_by_id(user_id: int, db: Session) -> Optional[models.User]:
    """
    Получает пользователя по его идентификатору.

    Эта функция выполняет запрос к базе данных, чтобы найти
    пользователя по его идентификатору.

    Args:
        user_id (int): Идентификатор пользователя.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        Optional[models.User]: Пользователь, если найден, иначе None.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user if user else None
