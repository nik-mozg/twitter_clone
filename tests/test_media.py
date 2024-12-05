import os
import time
from io import BytesIO
from typing import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Путь к тестовому изображению
TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test_image.png")


@pytest.fixture
def user() -> dict:
    """Фикстура для пользователя с API-ключом.

    Возвращает словарь с данными пользователя, который будет использоваться в тестах.

    Returns:
        dict: Словарь с данными пользователя, включая id, name и api-key.
    """
    user_data = {"id": 1, "name": "Test User", "api-key": "test-api-key"}
    return user_data


@pytest.fixture(scope="function")
def media_cleanup(user) -> Generator[None, None, None]:
    """Фикстура для очистки медиа-файлов после тестов.

    Очищает папку пользователя после выполнения теста.

    Returns:
        None
    """
    user_folder = os.path.join("app/media", str(user["id"]))
    yield
    if os.path.exists(user_folder):
        print(f"Cleaning up folder: {user_folder}")
        time.sleep(1)
        for file in os.listdir(user_folder):
            file_path = os.path.join(user_folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(user_folder)


def test_upload_media(user: dict) -> None:
    """Тест на загрузку медиа-файла.

    Проверяет, что медиа-файл можно загрузить с правильным
    API-ключом и что ответ содержит media_id.

    Args:
        user (dict): Данные пользователя, включая API-ключ.

    Returns:
        None
    """
    print(f"Testing with API key: {user['api-key']}")
    with open(TEST_IMAGE_PATH, "rb") as image_file:
        file = BytesIO(image_file.read())
        file.name = "test_image.png"
        response = client.post(
            "/api/medias",
            headers={"api-key": user["api-key"]},
            files={"file": ("test_image.png", file, "image/png")},
        )
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    assert response.status_code == 200
    assert response.json().get("result") is True
    assert isinstance(response.json().get("media_id"), int)


def test_upload_media_no_api_key() -> None:
    """Тест на загрузку медиа-файла без API-ключа.

    Проверяет, что при отсутствии API-ключа возвращается ошибка Unauthorized (403).

    Returns:
        None
    """
    with open(TEST_IMAGE_PATH, "rb") as image_file:
        file = BytesIO(image_file.read())
        file.name = "test_image.png"
        response = client.post(
            "/api/medias",
            files={"file": ("test_image.png", file, "image/png")},
        )
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    assert response.status_code == 403
    assert response.json() == {"detail": "Unauthorized"}


def test_get_media_file(user, media_cleanup) -> None:
    """Тест на получение медиа-файла.

    Проверяет, что можно получить медиа-файл по его имени
    и что файл корректно отображается.

    Returns:
        None
    """
    user_id = user["id"]
    media_filename = "test_image.png"

    # Создание папки для пользователя
    user_folder = os.path.join("app/media", str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    # Сохранение файла в папке пользователя
    file_path = os.path.join(user_folder, media_filename)
    with open(file_path, "wb") as f:
        with open(TEST_IMAGE_PATH, "rb") as image_file:
            f.write(image_file.read())

    # Пытаемся получить файл по правильному пути
    response = client.get(f"/app/media/{user_id}/{media_filename}")
    assert response.status_code == 200
    assert "test_image.png" in response.headers["Content-Disposition"]


def test_get_media_file_not_found() -> None:
    """Тест на попытку получения несуществующего медиа-файла.

    Проверяет, что при запросе несуществующего файла возвращается ошибка 404.

    Returns:
        None
    """
    response = client.get("/app/media/non_existent_file.png")
    assert response.status_code == 404


@patch("app.services.media_service.save_media", return_value=1)
def test_file_saved_with_unique_name(mock_save_media) -> None:
    """Тест на сохранение файла с уникальным именем.

    Проверяет, что медиа-файл сохраняется с уникальным именем
    (с добавлением времени в имени файла).

    Args:
        mock_save_media: Мок для функции сохранения медиа.

    Returns:
        None
    """
    user = {"api_key": "test-api-key", "id": 1, "name": "Test User"}
    print(f"Testing with API key: {user['api_key']}")
    with open(TEST_IMAGE_PATH, "rb") as image_file:
        file = BytesIO(image_file.read())
        file.name = "test_image.png"
        response = client.post(
            "/api/medias",
            headers={"api-key": user["api_key"]},
            files={"file": ("test_image.png", file, "image/png")},
        )
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")
    assert response.status_code == 200
    assert "result" in response.json()
    assert "media_id" in response.json()
    assert isinstance(response.json().get("media_id"), int)
    # Генерируем имя с учетом времени и проверяем сохранение
    new_filename = f"{int(time.time())}_{file.name}"
    user_folder = os.path.join("app/media", str(user["id"]))
    assert new_filename in os.listdir(
        user_folder
    )  # Проверка, что файл сохранен в папке пользователя
