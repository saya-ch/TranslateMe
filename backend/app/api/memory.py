"""
记忆管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import require_child_role
from app.schemas import (
    MemoryListResponse,
    MemoryDeleteResponse,
    MemoryApproveResponse,
)
from app.services.memory_service import MemoryService
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/memory", tags=["记忆"])


@router.get("/{child_id}", response_model=MemoryListResponse)
async def list_memory(
    child_id: str,
    current_user: dict = Depends(require_child_role),
    db: AsyncSession = Depends(get_db),
):
    # 权限校验：child 只能查看自己的记忆
    perm = PermissionService(db)
    if not await perm.child_owns_profile(current_user["user_id"], child_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该孩子档案",
        )
    service = MemoryService(db)
    items = await service.list_memory(child_id)
    return {"items": items}


@router.delete("/{child_id}/{memory_id}", response_model=MemoryDeleteResponse)
async def delete_memory(
    child_id: str,
    memory_id: str,
    current_user: dict = Depends(require_child_role),
    db: AsyncSession = Depends(get_db),
):
    # 权限校验
    perm = PermissionService(db)
    if not await perm.child_owns_profile(current_user["user_id"], child_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该孩子档案",
        )
    service = MemoryService(db)
    try:
        return await service.delete_memory(
            child_id=child_id,
            memory_id=memory_id,
            actor_user_id=current_user["user_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{child_id}/{memory_id}/approve", response_model=MemoryApproveResponse)
async def approve_level(
    child_id: str,
    memory_id: str,
    level: int = 2,
    current_user: dict = Depends(require_child_role),
    db: AsyncSession = Depends(get_db),
):
    # 权限校验
    perm = PermissionService(db)
    if not await perm.child_owns_profile(current_user["user_id"], child_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该孩子档案",
        )
    service = MemoryService(db)
    try:
        return await service.approve_memory_level(
            child_id=child_id,
            memory_id=memory_id,
            level=level,
            actor_user_id=current_user["user_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
