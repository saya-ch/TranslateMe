"""
家庭组和授权路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas import (
    FamilyGroupCreate,
    FamilyGroupResponse,
    MemberAdd,
    MemberRemoveResponse,
    ConsentCreate,
    ConsentResponse,
    ConsentRevokeResponse,
)
from app.services.family_group_service import FamilyGroupService

router = APIRouter(prefix="/family", tags=["家庭组"])


@router.post("/groups", response_model=FamilyGroupResponse)
async def create_group(
    req: FamilyGroupCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FamilyGroupService(db)
    try:
        return await service.create_or_get(
            child_user_id=req.child_user_id,
            guardian_user_id=req.guardian_user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/groups/{group_id}/members", response_model=dict)
async def add_member(
    group_id: str,
    req: MemberAdd,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FamilyGroupService(db)
    try:
        return await service.add_member(
            group_id=group_id,
            user_id=req.user_id,
            relation=req.relation,
            actor_user_id=current_user["user_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/groups/{group_id}/members/{member_user_id}", response_model=MemberRemoveResponse)
async def remove_member(
    group_id: str,
    member_user_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FamilyGroupService(db)
    try:
        return await service.remove_member(
            group_id=group_id,
            member_user_id=member_user_id,
            actor_user_id=current_user["user_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/consents", response_model=ConsentResponse)
async def create_consent(
    req: ConsentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FamilyGroupService(db)
    try:
        return await service.create_consent(
            actor_user_id=current_user["user_id"],
            child_id=req.child_id,
            scope=req.scope,
            purpose=req.purpose,
            source=req.source,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/consents/{consent_id}/revoke", response_model=ConsentRevokeResponse)
async def revoke_consent(
    consent_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = FamilyGroupService(db)
    try:
        return await service.revoke_consent(
            actor_user_id=current_user["user_id"],
            consent_id=consent_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
