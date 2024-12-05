from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import schemas
from app.db.database import get_db
from app.services import user_service

router = APIRouter()


@router.get("/api/users/me", response_model=schemas.UserResponse)
async def get_current_user(
    api_key: str = Header(...), db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Получение информации о текущем пользователе по API ключу.

    Аргументы:
    - api_key: API-ключ, переданный в заголовке запроса для авторизации пользователя.
    - db: Зависимость от сессии базы данных.

    Возвращает:
    - JSON-ответ, содержащий информацию о пользователе: ID, имя, подписчиков и подписок.
    """
    user = await user_service.get_user_by_api_key(api_key, db)
    user_info = await user_service.get_user_info(user.id, db)
    return JSONResponse(
        content={
            "result": True,
            "user": {
                "id": user_info["id"],
                "name": user_info["name"],
                "followers": [
                    {"id": follower["id"], "name": follower["name"]}
                    for follower in user_info["followers"]
                ],
                "following": [
                    {"id": following["id"], "name": following["name"]}
                    for following in user_info["following"]
                ],
            },
        }
    )


@router.get("/login", response_class=HTMLResponse)
async def login() -> RedirectResponse:
    """
    Перенаправление на главную страницу ("/").

    Возвращает:
    - Перенаправление на главную страницу.
    """
    return RedirectResponse(url="/")


@router.get("/api/users/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Получение информации о пользователе по его ID.

    Аргументы:
    - user_id: ID пользователя, информацию о котором нужно получить.
    - api_key: API-ключ, переданный в заголовке запроса для авторизации пользователя.
    - db: Зависимость от сессии базы данных.

    Возвращает:
    - JSON-ответ с информацией о пользователе: ID, имя, подписчики и подписки.
    """
    user = await user_service.get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    target_user = await user_service.get_user_by_id(user_id, db)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_info = await user_service.get_user_info(target_user.id, db)
    return JSONResponse(
        content={
            "result": True,
            "user": {
                "id": user_info["id"],
                "name": user_info["name"],
                "followers": [
                    {"id": follower["id"], "name": follower["name"]}
                    for follower in user_info["followers"]
                ],
                "following": [
                    {"id": following["id"], "name": following["name"]}
                    for following in user_info["following"]
                ],
            },
        }
    )


@router.post("/api/users/{user_id}/follow", response_model=dict)
async def follow_user(
    user_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
) -> dict:
    """
    Подписка на пользователя по его ID.

    Аргументы:
    - user_id: ID пользователя, на которого нужно подписаться.
    - api_key: API-ключ, переданный в заголовке запроса для авторизации пользователя.
    - db: Зависимость от сессии базы данных.

    Возвращает:
    - JSON-ответ с подтверждением результата операции.
    """
    user = await user_service.get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    target_user_info = await user_service.get_user_info(user_id, db)
    if not target_user_info:
        raise HTTPException(status_code=404, detail="User not found")
    await user_service.follow_user(user.id, target_user_info["id"], db)
    return {"result": True}


@router.delete("/api/users/{user_id}/follow", response_model=dict)
async def unfollow_user(
    user_id: int, api_key: str = Header(...), db: Session = Depends(get_db)
) -> dict:
    """
    Отписка от пользователя по его ID.

    Аргументы:
    - user_id: ID пользователя, от которого нужно отписаться.
    - api_key: API-ключ, переданный в заголовке запроса для авторизации пользователя.
    - db: Зависимость от сессии базы данных.

    Возвращает:
    - JSON-ответ с подтверждением результата операции.
    """
    user = await user_service.get_user_by_api_key(api_key, db)
    if not user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    target_user_info = await user_service.get_user_info(user_id, db)
    if not target_user_info:
        raise HTTPException(status_code=404, detail="User not found")
    await user_service.unfollow_user(user.id, target_user_info["id"], db)
    return {"result": True}
