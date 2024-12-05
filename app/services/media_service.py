from sqlalchemy.orm import Session

from app.db import models


async def save_media(file_location: str, user_id: int, db: Session) -> int:
    """
    Сохраняет информацию о медиа файле в базе данных.

    Эта функция принимает путь к файлу, идентификатор пользователя и
    объект базы данных, чтобы создать новую запись
    о медиа в таблице "Media". После добавления записи в базу данных
    возвращается идентификатор сохраненного медиа.

    Args:
        file_location (str): Путь к файлу, который должен быть сохранен.
        user_id (int): Идентификатор пользователя, который загружает медиа.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        int: Идентификатор сохраненного медиа.
    """
    media = models.Media(user_id=user_id, file_path=file_location)
    db.add(media)
    db.commit()
    db.refresh(media)
    return media.id
