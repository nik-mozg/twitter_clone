from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.services.user_service import get_user_info


async def create_tweet(
    tweet_data: str, user_id: int, tweet_media_ids: Optional[List[int]], db: Session
) -> int:
    """
    Создает новый твит и сохраняет его в базе данных.

    Эта функция принимает данные твита, идентификатор пользователя и список
    идентификаторов медиа файлов, если таковые имеются,
    и создает новый твит в базе данных. Также связывает медиа файлы с твитом,
    если они указаны.

    Args:
        tweet_data (str): Содержание твита.
        user_id (int): Идентификатор пользователя, который создает твит.
        tweet_media_ids (Optional[List[int]]): Список идентификаторов
        медиа файлов, прикрепленных к твиту.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        int: Идентификатор созданного твита.
    """
    new_tweet = models.Tweet(content=tweet_data, user_id=user_id)
    db.add(new_tweet)
    db.commit()
    db.refresh(new_tweet)
    if tweet_media_ids:
        for media_id in tweet_media_ids:
            media = db.query(models.Media).filter(models.Media.id == media_id).first()
            if not media:
                raise HTTPException(
                    status_code=400, detail=f"Media ID {media_id} does not exist."
                )
            tweet_media = models.TweetMedia(tweet_id=new_tweet.id, media_id=media_id)
            db.add(tweet_media)
    db.commit()
    return new_tweet.id


async def get_user_feed(user_id: int, db: Session) -> List[dict]:
    """
    Получает ленту твитов пользователя.

    Эта функция возвращает список твитов пользователя с прикрепленными
    медиа файлами и лайками.

    Args:
        user_id (int): Идентификатор пользователя, чью ленту нужно получить.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        List[dict]: Список твитов с прикрепленными медиа файлами и лайками.
    """
    tweets = db.query(models.Tweet).filter(models.Tweet.user_id == user_id).all()
    tweets_info = []
    for tweet in tweets:
        media_files = await get_media_files(tweet.id, db)
        tweet_data = {
            "id": tweet.id,
            "content": tweet.content,
            "attachments": media_files,
            "likes": await get_tweet_likes(tweet.id, db),
        }
        tweets_info.append(tweet_data)
    return tweets_info


async def get_media_files(tweet_id: int, db: Session) -> List[str]:
    """
    Получает список медиа файлов, прикрепленных к твиту.

    Эта функция возвращает пути к медиа файлам, прикрепленным к указанному твиту.

    Args:
        tweet_id (int): Идентификатор твита.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        List[str]: Список путей к медиа файлам.
    """
    media_links = (
        db.query(models.TweetMedia).filter(models.TweetMedia.tweet_id == tweet_id).all()
    )
    media_files = []
    for media_link in media_links:
        media_file = (
            db.query(models.Media)
            .filter(models.Media.id == media_link.media_id)
            .first()
        )
        if media_file:
            media_files.append(media_file.file_path)
    return media_files


async def get_tweet_likes(tweet_id: int, db: Session) -> List[dict]:
    """
    Получает список лайков для твита.

    Эта функция возвращает список пользователей, которые поставили лайк указанному твиту.

    Args:
        tweet_id (int): Идентификатор твита.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        List[dict]: Список пользователей, которые поставили лайк,
        с их именами и идентификаторами.
    """
    likes = (
        db.query(models.TweetLike).filter(models.TweetLike.tweet_id == tweet_id).all()
    )
    return [
        {"user_id": like.user_id, "name": await get_user_info(like.user_id, db)}
        for like in likes
    ]


async def get_tweet_attachments(tweet_id: int, db: Session) -> List[str]:
    """
    Получает список медиа файлов, прикрепленных к твиту.

    Эта функция возвращает пути к медиа файлам, прикрепленным к указанному твиту.

    Args:
        tweet_id (int): Идентификатор твита.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        List[str]: Список путей к медиа файлам.
    """
    media_links = []
    tweet_media = (
        db.query(models.TweetMedia).filter(models.TweetMedia.tweet_id == tweet_id).all()
    )
    for item in tweet_media:
        media = db.query(models.Media).filter(models.Media.id == item.media_id).first()
        if media:
            media_links.append(media.file_path)
    return media_links


async def like_tweet(tweet_id: int, user_id: int, db: Session) -> None:
    """
    Ставит лайк на твит.

    Эта функция проверяет, существует ли твит, и добавляет лайк
    от указанного пользователя.

    Args:
        tweet_id (int): Идентификатор твита.
        user_id (int): Идентификатор пользователя, ставящего лайк.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        None
    """
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise Exception("Tweet not found")
    like = models.TweetLike(user_id=user_id, tweet_id=tweet_id)
    db.add(like)
    db.commit()


async def unlike_tweet(tweet_id: int, user_id: int, db: Session) -> None:
    """
    Удаляет лайк с твита.

    Эта функция проверяет, существует ли твит и лайк, а затем удаляет
    лайк от указанного пользователя.

    Args:
        tweet_id (int): Идентификатор твита.
        user_id (int): Идентификатор пользователя, который убирает лайк.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        None
    """
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not tweet:
        raise Exception("Tweet not found")
    like = (
        db.query(models.TweetLike)
        .filter(
            models.TweetLike.tweet_id == tweet_id, models.TweetLike.user_id == user_id
        )
        .first()
    )
    db.delete(like)
    db.commit()


async def get_tweet_by_id(tweet_id: int, db: Session) -> Optional[models.Tweet]:
    """
    Получает твит по его идентификатору.

    Эта функция возвращает твит с указанным идентификатором, если он существует.

    Args:
        tweet_id (int): Идентификатор твита.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        Optional[models.Tweet]: Твит, если он найден, иначе None.
    """
    return db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()


async def delete_tweet(tweet_id: int, db: Session) -> None:
    """
    Удаляет твит.

    Эта функция проверяет, существует ли твит с указанным идентификатором
    и удаляет его из базы данных.

    Args:
        tweet_id (int): Идентификатор твита, который нужно удалить.
        db (Session): Сессия SQLAlchemy для работы с базой данных.

    Returns:
        None
    """
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if tweet:
        db.delete(tweet)
        db.commit()
