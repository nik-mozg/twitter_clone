from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class MediaResponse(BaseModel):
    """
    Модель ответа для медиа.

    Атрибуты:
    - result (bool): Указывает успешность операции.
    - media_id (int): Идентификатор загруженного медиа.

    Возвращаемое значение:
    - MediaResponse: Модель, которая возвращает результат и идентификатор медиа.
    """

    result: bool
    media_id: int


class TweetBase(BaseModel):
    """
    Базовая модель твита.

    Атрибуты:
    - content (str): Содержимое твита.
    - media_id (Optional[int]): Идентификатор медиа,
    прикрепленного к твиту (необязательное поле).

    Возвращаемое значение:
    - TweetBase: Модель твита с обязательным содержанием и необязательным медиа.
    """

    content: str
    media_id: Optional[int] = None


class TweetCreate(BaseModel):
    """
    Модель для создания нового твита.

    Атрибуты:
    - tweet_data (str): Содержимое твита.
    - tweet_media_ids (Optional[List[int]]): Список идентификаторов медиа,
    прикрепленных к твиту (необязательное поле).

    Возвращаемое значение:
    - TweetCreate: Модель для создания твита с обязательным
    содержанием и необязательными медиа.
    """

    tweet_data: str
    tweet_media_ids: Optional[List[int]] = []


class TweetResponse(BaseModel):
    """
    Модель для ответа на запрос о твите.

    Атрибуты:
    - id (int): Идентификатор твита.
    - content (str): Содержимое твита.
    - attachments (List[str]): Список путей к прикрепленным медиафайлам.
    - author (dict): Информация о пользователе, который опубликовал твит.
    - likes (List[dict]): Список пользователей, поставивших лайк этому твиту.

    Возвращаемое значение:
    - TweetResponse: Модель, представляющая твит с дополнительной информацией о медиа,
    авторе и лайках.
    """

    id: int
    content: str
    attachments: List[str]
    author: dict
    likes: List[dict]

    model_config = ConfigDict(from_attributes=True)


class TweetListResponse(BaseModel):
    """
    Модель для ответа с несколькими твитами.

    Атрибуты:
    - result (bool): Указывает успешность операции.
    - tweets (List[TweetResponse]): Список твитов.

    Возвращаемое значение:
    - TweetListResponse: Модель с результатом операции и списком твитов.
    """

    result: bool
    tweets: List[TweetResponse]


class UserBase(BaseModel):
    """
    Базовая модель пользователя.

    Атрибуты:
    - name (str): Имя пользователя.

    Возвращаемое значение:
    - UserBase: Модель для представления данных пользователя с именем.
    """

    name: str


class UserResponse(UserBase):
    """
    Модель для ответа о пользователе.

    Атрибуты:
    - id (int): Идентификатор пользователя.
    - followers (List[UserBase]): Список подписчиков пользователя.
    - following (List[UserBase]): Список пользователей,
    на которых подписан данный пользователь.

    Возвращаемое значение:
    - UserResponse: Модель, представляющая пользователя и его подписчиков.
    """

    id: int
    followers: List[UserBase] = []
    following: List[UserBase] = []

    model_config = ConfigDict(from_attributes=True)


class UserFollowResponse(BaseModel):
    """
    Модель ответа на запрос о подписке/отписке пользователя.

    Атрибуты:
    - result (bool): Указывает успешность операции.

    Возвращаемое значение:
    - UserFollowResponse: Модель, представляющая результат операции подписки или отписки.
    """

    result: bool


class TweetLikeResponse(BaseModel):
    """
    Модель ответа на запрос о лайке твита.

    Атрибуты:
    - result (bool): Указывает успешность операции.

    Возвращаемое значение:
    - TweetLikeResponse: Модель, представляющая результат операции лайка твита.
    """

    result: bool


class MediaListResponse(BaseModel):
    """
    Модель ответа с медиафайлами.

    Атрибуты:
    - result (bool): Указывает успешность операции.
    - media (List[MediaResponse]): Список медиафайлов.

    Возвращаемое значение:
    - MediaListResponse: Модель, представляющая список медиафайлов с результатом операции.
    """

    result: bool
    media: List[MediaResponse]
