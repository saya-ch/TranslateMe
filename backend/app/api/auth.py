"""
认证路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    MeResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        service = AuthService(db)
        result = await service.register(
            username=req.username,
            display_name=req.display_name,
            role=req.role,
            password=req.password,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.login(req.username, req.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    return result


@router.get("/me", response_model=MeResponse)
async def me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    try:
        return await service.get_me(current_user["user_id"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
