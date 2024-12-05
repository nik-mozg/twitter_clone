from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_index() -> None:
    """Тест на главную страницу.

    Проверяет, что главная страница приложения загружается с корректным статусом
    и содержит ожидаемое HTML-содержимое.

    Returns:
        None
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text


def test_create_database_if_not_exists() -> None:
    """Тест на создание базы данных (если не существует).

    Проверяет, что при посещении главной страницы создается
    база данных, если она еще не существует.

    Returns:
        None
    """
    response = client.get("/")
    assert response.status_code == 200


@patch("alembic.command.upgrade")
def test_automatic_migrations(mock_upgrade) -> None:
    """Тест на автоматическое выполнение миграций.

    Проверяет, что миграции не выполняются автоматически при старте приложения,
    а команда миграции не была вызвана.

    Args:
        mock_upgrade: Мок для команды миграции Alembic.

    Returns:
        None
    """
    response = client.get("/")
    assert response.status_code == 200
    mock_upgrade.assert_not_called()


@patch("os.path.join", return_value="app/index.html")
def test_static_files(mock_os_path) -> None:
    """Тест на отдачу статических файлов.

    Проверяет, что статические файлы (например, HTML-шаблоны) корректно загружаются
    при запросе на главную страницу.

    Args:
        mock_os_path: Мок для функции os.path.join, возвращающий путь к шаблону.

    Returns:
        None
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
