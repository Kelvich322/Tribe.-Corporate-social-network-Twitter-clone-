from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.crud.followers import delete_follow_association
from app.crud.followers import follow_user as crud_follow_user
from app.crud.user import get_user_by_id as crud_get_user_by_id
from app.models import User
from app.schemas.responses import ExceptionResponse, SuccessResponse
from app.schemas.user import UserInfoSchema, UserSuccessResponse

user_routers = APIRouter(prefix="/api", tags=["users"])


@user_routers.get(
    "/users/me",
    response_model=UserSuccessResponse,
    responses={
        200: {
            "model": UserSuccessResponse,
            "description": "Successful response with user data",
        },
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
        422: {"model": ExceptionResponse, "description": "Validation error"},
    },
)
async def get_user_by_api(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Получить информацию о текущем аутентифицированном пользователе.
    """
    if user:
        user_schema = UserInfoSchema.model_validate(user)
        return UserSuccessResponse(result=True, user=user_schema)
    raise HTTPException(status_code=401, detail="Invalid API Key")


@user_routers.get(
    "/users/{id}",
    response_model=UserSuccessResponse,
    responses={
        200: {
            "model": UserSuccessResponse,
            "description": "Successful response with user data",
        },
        404: {"model": ExceptionResponse, "description": "User not found"},
        422: {"model": ExceptionResponse, "description": "Validation error"},
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
    },
)
async def get_user_by_id(id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить информацию о пользователе по его ID.
    """
    user = await crud_get_user_by_id(user_id=id, db=db)
    if user:
        user_schema = UserInfoSchema.model_validate(user)
        return UserSuccessResponse(result=True, user=user_schema)
    raise HTTPException(status_code=404, detail=f"User with ID {id} not found")


@user_routers.post(
    "/users/{id}/follow",
    status_code=201,
    response_model=SuccessResponse,
    responses={
        201: {"model": SuccessResponse, "description": "Successful response"},
        400: {"model": ExceptionResponse, "description": "Bad request data"},
        422: {"model": ExceptionResponse, "description": "Validation error"},
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
    },
)
async def follow_user(
    id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Подписаться на пользователя.
    """
    if id == user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    target_user = await crud_get_user_by_id(user_id=id, db=db)
    if not target_user:
        raise HTTPException(status_code=404, detail="User to follow not found")

    result = await crud_follow_user(
        db=db, following_id=target_user.id, follower_id=user.id
    )
    if result:
        return SuccessResponse(result=True)
    raise HTTPException(status_code=400, detail="Bad request data")


@user_routers.delete(
    "/users/{id}/follow",
    response_model=SuccessResponse,
    responses={
        200: {
            "model": SuccessResponse,
            "description": "Successful unfollowing from user",
        },
        400: {"model": ExceptionResponse, "description": "Bad request data"},
        422: {"model": ExceptionResponse, "description": "Validation error"},
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
    },
)
async def unfollow_user(
    id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Отписаться от пользователя.
    """
    follower_id = user.id
    result = await delete_follow_association(
        db=db, following_id=id, follower_id=follower_id
    )
    if result:
        return SuccessResponse(result=True)
    raise HTTPException(status_code=400, detail="Bad request data")
