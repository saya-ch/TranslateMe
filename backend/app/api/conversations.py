"""
会话/聊天路由（孩子发送消息、草稿确认）
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.session import get_db
from app.api.deps import require_child_role, require_guardian_role, get_current_user
from app.services.permission_service import PermissionService
from app.schemas import (
    ChatRequest,
    ChatResponse,
    DraftConfirmRequest,
    DraftConfirmResponse,
    ShareRevokeResponse,
    ReplyRequest,
    ReplyResponse,
    InboxListResponse,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["会话"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    current_user: dict = Depends(require_child_role),
    db: AsyncSession = Depends(get_db),
):
    # 权限校验：孩子只能访问自己的 child_profile
    perm = PermissionService(db)
    if not await perm.child_owns_profile(current_user["user_id"], req.child_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该孩子档案")

    service = ConversationService(db)
    try:
        return await service.process_child_message(
            user_id=current_user["user_id"],
            conversation_id=req.conversation_id,
            child_id=req.child_id,
            text=req.text,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/drafts/{draft_id}/confirm", response_model=DraftConfirmResponse)
async def confirm_draft(
    draft_id: str,
    req: DraftConfirmRequest,
    current_user: dict = Depends(require_child_role),
    db: AsyncSession = Depends(get_db),
):
    service = ConversationService(db)
    try:
        # service 内部会校验 draft 所属的 child_id 是否属于当前用户
        result = await service.confirm_and_share(
            user_id=current_user["user_id"],
            draft_id=draft_id,
            to_role=req.to_role,
            level=req.level,
        )
        return result
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/shares/{share_id}/revoke", response_model=ShareRevokeResponse)
async def revoke_share(
    share_id: str,
    current_user: dict = Depends(require_child_role),
    db: AsyncSession = Depends(get_db),
):
    service = ConversationService(db)
    try:
        return await service.revoke_share(
            user_id=current_user["user_id"],
            share_id=share_id,
        )
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reply", response_model=ReplyResponse)
async def reply(
    req: ReplyRequest,
    current_user: dict = Depends(require_guardian_role),
    db: AsyncSession = Depends(get_db),
):
    # 权限校验：家长/老师必须在该孩子的家庭组中
    perm = PermissionService(db)
    if not await perm.user_in_child_group(current_user["user_id"], req.child_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该孩子档案")

    service = ConversationService(db)
    try:
        return await service.reply_to_child(
            user_id=current_user["user_id"],
            user_role=current_user["role"],
            child_id=req.child_id,
            to_role=req.to_role,
            body=req.body,
            source_inbox_id=req.source_inbox_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/inbox", response_model=InboxListResponse)
async def inbox(
    child_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    perm = PermissionService(db)

    # 如果指定了 child_id，校验权限
    if child_id:
        if not await perm.user_can_access_child(current_user["user_id"], current_user["role"], child_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该孩子档案")

    service = ConversationService(db)
    items = await service.inbox_list(
        user_id=current_user["user_id"],
        user_role=current_user["role"],
        child_id=child_id,
    )
    return {"items": items, "total": len(items)}
