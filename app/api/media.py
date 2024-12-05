#  api/media.py
import os
import shutil
import time
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db import schemas
from app.db.database import get_db
from app.services import media_service, user_service

router = APIRouter()


@router.get("/app/media/{user_id}/{filename}")
async def get_media_file(user_id: int, filename: str) -> FileResponse:
    """
    Получает медиафайл по имени файла для конкретного пользователя.
    Параметры:
    - user_id (int): ID пользователя, для которого нужно получить файл.
    - filename (str): Имя файла, который нужно вернуть.

    Возвращаемое значение:
    - FileResponse: Файл в формате ответа.

    Исключения:
    - HTTP 404: Если файл не найден.
    """
    # Путь к папке пользователя
    user_folder = os.path.join("app/media", str(user_id))
    # Полный путь к файлу
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        # Кодируем имя файла в безопасный для URL вид
        encoded_filename = quote(filename)
        return FileResponse(
            file_path,
            headers={"Content-Disposition": f"attachment; filename={encoded_filename}"},
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")


@router.post("/api/medias", response_model=schemas.MediaResponse)
async def upload_media(
    api_key: str = Header(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    """
    Загружает медиафайл, генерирует уникальное имя файла и сохраняет его.
    Параметры:
    - api_key (str): API-ключ пользователя для аутентификации.
    - file (UploadFile): Загружаемый медиафайл.
    - db (Session): Сессия базы данных для выполнения запросов.
    Возвращаемое значение:
    - dict: Возвращает объект с результатом загрузки и идентификатором медиафайла.
    Исключения:
    - HTTP 403: Если API-ключ не действителен.
    - HTTP 500: Если произошла ошибка при загрузке файла.
    """
    if api_key is None:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Получаем пользователя по API ключу
    user = await user_service.get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Создаем уникальное имя для файла на основе временной метки
    timestamp = int(time.time())
    new_filename = f"{timestamp}_{file.filename}"

    # Создаем папку для пользователя, если она еще не существует
    user_folder = os.path.join("app/media", str(user.id))  # Папка с ID пользователя
    os.makedirs(user_folder, exist_ok=True)  # Создание папки, если ее нет

    # Путь к файлу внутри папки пользователя
    file_location = os.path.join(user_folder, new_filename)

    # Сохраняем файл на диск
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # Сохраняем информацию о медиафайле в базе данных
    media_id = await media_service.save_media(file_location, user.id, db)

    # Возвращаем успешный ответ с ID медиафайла
    return {"result": True, "media_id": media_id}
