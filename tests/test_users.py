from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.services.user_service.get_user_by_api_key")
@patch("app.services.user_service.get_user_info")
def test_get_current_user(mock_get_user_info, mock_get_user):
    """Тест на получение текущего пользователя.

    Проверяет, что API корректно возвращает информацию о текущем
    пользователе по API-ключу.

    Args:
        mock_get_user_info (MagicMock): Мок метода получения информации о пользователе.
        mock_get_user (MagicMock): Мок метода получения пользователя по API-ключу.

    Returns:
        None
    """
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.name = "Test User"
    mock_user.api_key = "test-api-key"
    mock_get_user.return_value = mock_user
    mock_get_user_info.return_value = {
        "id": 1,
        "name": "Test User",
        "followers": [{"id": 2, "name": "Follower 1"}],
        "following": [{"id": 3, "name": "Following 1"}],
    }
    response = client.get("/api/users/me", headers={"api-key": "test-api-key"})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["result"] is True
    assert response_json["user"]["id"] == 1
    assert response_json["user"]["name"] == "Test User"
    assert len(response_json["user"]["followers"]) == 1
    assert len(response_json["user"]["following"]) == 1


@patch("app.services.user_service.get_user_by_api_key")
@patch("app.services.user_service.get_user_info")
@patch("app.services.user_service.get_user_by_id")
def test_get_user(mock_get_user_by_id, mock_get_user_info, mock_get_user):
    """Тест на получение информации о пользователе по ID.

    Проверяет, что API корректно возвращает информацию о пользователе по его ID.

    Args:
        mock_get_user_by_id (MagicMock): Мок метода получения пользователя по ID.
        mock_get_user_info (MagicMock): Мок метода получения информации о пользователе.
        mock_get_user (MagicMock): Мок метода получения пользователя по API-ключу.

    Returns:
        None
    """
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.api_key = "test-api-key"
    mock_get_user.return_value = mock_user
    mock_target_user = MagicMock()
    mock_target_user.id = 2
    mock_target_user.name = "Target User"
    mock_get_user_by_id.return_value = mock_target_user
    mock_get_user_info.return_value = {
        "id": 2,
        "name": "Target User",
        "followers": [{"id": 1, "name": "Test User"}],
        "following": [{"id": 3, "name": "Following 1"}],
    }
    response = client.get("/api/users/2", headers={"api-key": "test-api-key"})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["result"] is True
    assert response_json["user"]["id"] == 2
    assert response_json["user"]["name"] == "Target User"


@patch("app.services.user_service.get_user_by_api_key")
@patch("app.services.user_service.get_user_info")
@patch("app.services.user_service.follow_user")
def test_follow_user(mock_follow_user, mock_get_user_info, mock_get_user):
    """Тест на подписку на пользователя.

    Проверяет, что API корректно подписывает пользователя на другого пользователя.

    Args:
        mock_follow_user (MagicMock): Мок метода подписки на пользователя.
        mock_get_user_info (MagicMock): Мок метода получения информации о пользователе.
        mock_get_user (MagicMock): Мок метода получения пользователя по API-ключу.

    Returns:
        None
    """
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.api_key = "test-api-key"
    mock_get_user.return_value = mock_user
    mock_target_user_info = {"id": 2, "name": "Target User"}
    mock_get_user_info.return_value = mock_target_user_info
    response = client.post("/api/users/2/follow", headers={"api-key": "test-api-key"})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["result"] is True


@patch("app.services.user_service.get_user_by_api_key")
@patch("app.services.user_service.get_user_info")
@patch("app.services.user_service.unfollow_user")
def test_unfollow_user(mock_unfollow_user, mock_get_user_info, mock_get_user):
    """Тест на отписку от пользователя.

    Проверяет, что API корректно отписывает пользователя от другого пользователя.

    Args:
        mock_unfollow_user (MagicMock): Мок метода отписки от пользователя.
        mock_get_user_info (MagicMock): Мок метода получения информации о пользователе.
        mock_get_user (MagicMock): Мок метода получения пользователя по API-ключу.

    Returns:
        None
    """
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.api_key = "test-api-key"
    mock_get_user.return_value = mock_user
    mock_target_user_info = {"id": 2, "name": "Target User"}
    mock_get_user_info.return_value = mock_target_user_info
    response = client.delete("/api/users/2/follow", headers={"api-key": "test-api-key"})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["result"] is True
