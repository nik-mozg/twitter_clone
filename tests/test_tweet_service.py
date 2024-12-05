from unittest.mock import MagicMock

import pytest

from app.services.tweet_service import (
    create_tweet,
    delete_tweet,
    get_tweet_by_id,
    like_tweet,
    unlike_tweet,
)


# Создание моков для базы данных и пользователя
@pytest.fixture
def mock_db():
    """Создание мокированного объекта базы данных.

    Returns:
        MagicMock: Мок базы данных.
    """
    db = MagicMock()
    yield db


@pytest.fixture
def mock_user():
    """Создание мокированного пользователя.

    Returns:
        MagicMock: Мок пользователя с id=1.
    """
    user = MagicMock()
    user.id = 1
    user.name = "Test User"
    return user


@pytest.fixture
def tweet_data():
    """Данные для создания твита.

    Returns:
        dict: Словарь с данными твита.
    """
    return {"tweet_data": "This is a test tweet", "tweet_media_ids": [1, 2]}


@pytest.mark.asyncio
async def test_create_tweet(mock_db, tweet_data, mock_user):
    """Тест на создание твита.

    Проверяет, что твит создается корректно, и что его ID правильно возвращается.

    Args:
        mock_db (MagicMock): Мок базы данных.
        tweet_data (dict): Данные для твита.
        mock_user (MagicMock): Мок пользователя.

    Returns:
        None
    """
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Мокаем создание твита с ID 123
    mock_db.add.side_effect = lambda x: setattr(x, "id", 123)
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock(id=1)

    # Создаем твит
    tweet_id = await create_tweet(
        tweet_data["tweet_data"], mock_user.id, tweet_data["tweet_media_ids"], mock_db
    )

    # Проверки
    assert tweet_id is not None
    assert tweet_id == 123
    mock_db.add.assert_called()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_like_tweet(mock_db, mock_user):
    """Тест на лайк твита.

    Проверяет, что лайк твита добавляется правильно.

    Args:
        mock_db (MagicMock): Мок базы данных.
        mock_user (MagicMock): Мок пользователя.

    Returns:
        None
    """
    mock_tweet = MagicMock(id=1, user_id=mock_user.id)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_tweet
    mock_db.add.return_value = None
    mock_db.commit.return_value = None

    # Лайк твита
    await like_tweet(mock_tweet.id, mock_user.id, mock_db)

    # Проверки
    mock_db.add.assert_called()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_unlike_tweet(mock_db, mock_user):
    """Тест на удаление лайка с твита.

    Проверяет, что лайк твита удаляется корректно.

    Args:
        mock_db (MagicMock): Мок базы данных.
        mock_user (MagicMock): Мок пользователя.

    Returns:
        None
    """
    mock_tweet = MagicMock(id=1, user_id=mock_user.id)
    mock_like = MagicMock(user_id=mock_user.id, tweet_id=mock_tweet.id)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_like
    mock_db.delete.return_value = None
    mock_db.commit.return_value = None

    # Удаление лайка с твита
    await unlike_tweet(mock_tweet.id, mock_user.id, mock_db)

    # Проверки
    mock_db.delete.assert_called()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_get_tweet_by_id(mock_db):
    """Тест на получение твита по ID.

    Проверяет, что твит возвращается корректно по ID.

    Args:
        mock_db (MagicMock): Мок базы данных.

    Returns:
        None
    """
    mock_tweet = MagicMock(id=1, content="This is a test tweet")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_tweet

    # Получаем твит по ID
    tweet = await get_tweet_by_id(1, mock_db)

    # Проверки
    assert tweet is not None
    assert tweet.id == 1


@pytest.mark.asyncio
async def test_delete_tweet(mock_db):
    """Тест на удаление твита.

    Проверяет, что твит удаляется корректно по ID.

    Args:
        mock_db (MagicMock): Мок базы данных.

    Returns:
        None
    """
    mock_tweet = MagicMock(id=1, content="This is a test tweet")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_tweet
    mock_db.delete.return_value = None
    mock_db.commit.return_value = None

    # Удаляем твит
    await delete_tweet(1, mock_db)

    # Проверки
    mock_db.delete.assert_called()
    mock_db.commit.assert_called()
