from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.db.models import Tweet, User
from app.main import app

client = TestClient(app)


def test_create_and_delete_tweet():
    """Тест на создание и удаление твита.

    Проверяет, что твит создается и затем удаляется корректно для
    авторизованного пользователя.

    Returns:
        None
    """
    tweet_data = {"tweet_data": "This is a test tweet", "tweet_media_ids": []}
    response = client.post(
        "/api/tweets", json=tweet_data, headers={"api-key": "test-api-key"}
    )
    assert response.status_code == 200
    response_json = response.json()
    assert "id" in response_json
    assert isinstance(response_json["id"], int)
    tweet_id = response_json["id"]
    response = client.delete(
        f"/api/tweets/{tweet_id}", headers={"api-key": "test-api-key"}
    )
    assert response.status_code == 200


def create_or_get_test_user(api_key: str, name: str) -> User:
    """Создание или получение тестового пользователя по ключу API.

    Если пользователь с указанным ключом API не найден, то он будет создан.

    Args:
        api_key (str): API ключ пользователя.
        name (str): Имя пользователя.

    Returns:
        User: Пользователь, созданный или найденный в базе данных.
    """
    db = SessionLocal()
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        user = User(name=name, api_key=api_key)
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
    return user


def create_test_tweet(user_id: int) -> Tweet:
    """Создание тестового твита для пользователя.

    Args:
        user_id (int): ID пользователя, который создает твит.

    Returns:
        Tweet: Созданный твит.
    """
    db = SessionLocal()
    tweet = Tweet(content="This is a test tweet", user_id=user_id)
    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    return tweet
