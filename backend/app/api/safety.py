"""
安全事件路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import require_child_role
from app.schemas import (
    SafetyCheckRequest,
    SafetyCheckResponse,
    SafetyResolveRequest,
    SafetyResolveResponse,
)
from app.services.safety_service import SafetyService

router = APIRouter(prefix="/safety", tags=["安全"])


@router.post("/check", response_model=SafetyCheckResponse)
async def check_text(
    req: SafetyCheckRequest,
    current_user: dict = Depends(require_child_role),
    db: AsyncSession = Depends(get_db),
):
    service = SafetyService(db)
    return service.check_text(req.text)


@router.post("/events/{event_id}/resolve", response_model=SafetyResolveResponse)
async def resolve_event(
    event_id: str,
    req: SafetyResolveRequest,
    current_user: dict = Depends(require_child_role),
    db: AsyncSession = Depends(get_db),
):
    service = SafetyService(db)
    try:
        return await service.resolve_event(
            user_id=current_user["user_id"],
            safety_event_id=event_id,
            branch=req.branch,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
