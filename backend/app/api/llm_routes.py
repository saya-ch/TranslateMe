"""
家长/老师向 AI 提问的路由 - 带权限防火墙
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from app.db.session import get_db
from app.api.deps import require_guardian_role
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/llm", tags=["LLM"])


class ParentAskRequest(BaseModel):
    child_id: str
    question: str = Field(min_length=1, max_length=2000)


class TeacherAskRequest(BaseModel):
    child_id: str
    observation: str = Field(min_length=1, max_length=2000)


@router.post("/parent-ask")
async def parent_ask(
    req: ParentAskRequest,
    current_user: dict = Depends(require_guardian_role),
    db: AsyncSession = Depends(get_db),
):
    # 权限校验：guardian 必须在孩子家庭组内
    perm = PermissionService(db)
    if not await perm.user_in_child_group(current_user["user_id"], req.child_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该孩子档案",
        )

    orchestrator = LLMOrchestrator(db)
    return await orchestrator.parent_ask(
        user_id=current_user["user_id"],
        child_id=req.child_id,
        question=req.question,
    )


@router.post("/teacher-ask")
async def teacher_ask(
    req: TeacherAskRequest,
    current_user: dict = Depends(require_guardian_role),
    db: AsyncSession = Depends(get_db),
):
    # 权限校验：guardian 必须在孩子家庭组内
    perm = PermissionService(db)
    if not await perm.user_in_child_group(current_user["user_id"], req.child_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该孩子档案",
        )

    orchestrator = LLMOrchestrator(db)
    return await orchestrator.teacher_ask(
        user_id=current_user["user_id"],
        child_id=req.child_id,
        observation=req.observation,
    )
