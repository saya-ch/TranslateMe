"""
FastAPI 依赖注入 + 权限校验
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_jwt
from app.services.permission_service import PermissionService

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭证",
        )

    try:
        payload = decode_jwt(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效或已过期的 token",
            )
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
        )


async def require_child_role(
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "child":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要孩子角色",
        )
    return current_user


async def require_guardian_role(
    current_user: dict = Depends(get_current_user),
):
    role = current_user.get("role")
    if role not in ("parent", "teacher", "counselor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要家长/老师/心理老师角色",
        )
    return current_user


async def verify_child_access(
    child_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """校验当前用户是否有权访问该 child_id"""
    perm = PermissionService(db)
    has_access = await perm.user_can_access_child(
        current_user["user_id"], current_user["role"], child_id
    )
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该孩子档案",
        )
    return current_user
