import os

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload

from app.db import models, schemas
from app.db.database import get_db
from app.services import tweet_service, user_service
from app.services.user_service import get_user_by_api_key

router = APIRouter()


@router.get("/api/tweets", response_model=schemas.TweetListResponse)
async def get_tweets(
    api_key: str = Header(...), db: Session = Depends(get_db)
) -> schemas.TweetListResponse:
    """
    Получение списка твитов для авторизованного пользователя.

    Аргументы:
    - api_key: API-ключ, переданный в заголовке запроса для авторизации пользователя.
    - db: Зависимость от сессии базы данных.

    Возвращает:
    - JSON-ответ, содержащий список твитов с вложениями, данными автора и лайками,
    отсортированный по лайкам.
    """
    user = await get_user_by_api_key(api_key, db)
    if not user:
        return JSONResponse(
            content={
                "result": False,
                "error_type": "Unauthorized",
                "error_message": "Invalid API key",
            },
            status_code=403,
        )
    try:
        tweets = (
            db.query(models.Tweet)
            .options(
                joinedload(models.Tweet.author), joinedload(models.Tweet.media_links)
            )
            .all()
        )
        tweet_responses = []
        for tweet in tweets:
            media_files = await tweet_service.get_tweet_attachments(tweet.id, db)
            likes = await tweet_service.get_tweet_likes(tweet.id, db)
            author = tweet.author if tweet.author else {"id": None, "name": None}
            tweet_responses.append(
                {
                    "result": True,
                    "id": tweet.id,
                    "content": tweet.content,
                    "attachments": media_files,
                    "author": {"id": author.id, "name": author.name},
                    "likes": likes,
                }
            )
        # Сортировка твитов по количеству лайков (по убыванию)
        tweet_responses.sort(key=lambda x: len(x["likes"]), reverse=True)

        return schemas.TweetListResponse(result=True, tweets=tweet_responses)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JSONResponse(
            content={
                "result": False,
                "error_type": "InternalServerError",
                "error_message": str(e),
            },
            status_code=500,
        )


@router.delete("/api/tweets/{tweet_id}", response_model=dict)
async def delete_tweet(
    tweet_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
) -> dict:
    """
    Удаляет конкретный твит по ID.

    Аргументы:
    - tweet_id: ID твита для удаления.
    - api_key: API-ключ, переданный в заголовке запроса для авторизации пользователя.
    - db: Зависимость от сессии базы данных.

    Возвращает:
    - JSON-ответ с подтверждением результата операции.
    """
    user = await user_service.get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    tweet = await tweet_service.get_tweet_by_id(tweet_id, db)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    if tweet.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own tweets"
        )
    media_files = (
        db.query(models.TweetMedia).filter(models.TweetMedia.tweet_id == tweet_id).all()
    )
    for media_file in media_files:
        db.delete(media_file)
        media = (
            db.query(models.Media)
            .filter(models.Media.id == media_file.media_id)
            .first()
        )
        if media and os.path.exists(media.file_path):
            os.remove(media.file_path)
            db.delete(media)
    db.delete(tweet)
    db.commit()
    return {"result": True}


@router.post("/api/tweets/{tweet_id}/likes", response_model=dict)
async def like_tweet(
    tweet_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
) -> dict:
    """
    Ставит лайк на твит для авторизованного пользователя.

    Аргументы:
    - tweet_id: ID твита, который нужно лайкнуть.
    - api_key: API-ключ, переданный в заголовке запроса для авторизации пользователя.
    - db: Зависимость от сессии базы данных.

    Возвращает:
    - JSON-ответ с подтверждением результата операции.
    """
    user = await get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    await tweet_service.like_tweet(tweet_id, user.id, db)
    return {"result": True}


@router.delete("/api/tweets/{tweet_id}/likes", response_model=dict)
async def unlike_tweet(
    tweet_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
) -> dict:
    """
    Снимает лайк с твита для авторизованного пользователя.

    Аргументы:
    - tweet_id: ID твита, с которого нужно снять лайк.
    - api_key: API-ключ, переданный в заголовке запроса для авторизации пользователя.
    - db: Зависимость от сессии базы данных.

    Возвращает:
    - JSON-ответ с подтверждением результата операции.
    """
    user = await get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    await tweet_service.unlike_tweet(tweet_id, user.id, db)
    return {"result": True}


@router.post("/api/tweets", response_model=schemas.TweetResponse)
async def create_tweet(
    tweet: schemas.TweetCreate,
    api_key: str = Header(...),
    db: Session = Depends(get_db),
) -> dict:
    """
    Создает новый твит для авторизованного пользователя.

    Аргументы:
    - tweet: Данные для создания твита, включая текст и медиа.
    - api_key: API-ключ, переданный в заголовке запроса для авторизации пользователя.
    - db: Зависимость от сессии базы данных.

    Возвращает:
    - JSON-ответ, содержащий созданный твит с деталями.
    """
    user = await get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    tweet_id = await tweet_service.create_tweet(
        tweet_data=tweet.tweet_data,
        user_id=user.id,
        tweet_media_ids=tweet.tweet_media_ids,
        db=db,
    )
    created_tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()
    if not created_tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    media_files = await tweet_service.get_tweet_attachments(created_tweet.id, db)
    likes = await tweet_service.get_tweet_likes(created_tweet.id, db)
    response = {
        "id": created_tweet.id,
        "content": created_tweet.content,
        "attachments": media_files,
        "author": {"id": created_tweet.author.id, "name": created_tweet.author.name},
        "likes": likes,
    }
    return response
