"""
家庭组服务 - 添加/删除成员
"""

import uuid
import json
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.family_groups import FamilyGroup
from app.db.models.group_members import GroupMember
from app.db.models.child_profiles import ChildProfile
from app.db.models.consents import Consent
from app.db.models.audit_logs import AuditLog


class FamilyGroupService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_or_get(self, child_user_id: str, guardian_user_id: str) -> Dict[str, Any]:
        # 查找孩子档案
        child_stmt = select(ChildProfile).where(ChildProfile.user_id == child_user_id)
        child = (await self.db.execute(child_stmt)).scalar_one_or_none()
        if not child:
            raise ValueError("孩子档案不存在")

        # 查找已存在的家庭组
        group_stmt = select(FamilyGroup).where(FamilyGroup.child_id == child.id)
        group = (await self.db.execute(group_stmt)).scalar_one_or_none()

        if not group:
            group = FamilyGroup(
                id=str(uuid.uuid4()),
                child_id=child.id,
                name=f"{child.display_name}的家庭组",
            )
            self.db.add(group)
            await self.db.flush()

            # 孩子自己
            self.db.add(
                GroupMember(
                    id=str(uuid.uuid4()),
                    group_id=group.id,
                    user_id=child_user_id,
                    relation="self",
                )
            )
            # 监护人
            self.db.add(
                GroupMember(
                    id=str(uuid.uuid4()),
                    group_id=group.id,
                    user_id=guardian_user_id,
                    relation="guardian",
                )
            )

        # 成员列表
        members_stmt = select(GroupMember).where(GroupMember.group_id == group.id)
        members = (await self.db.execute(members_stmt)).scalars().all()

        return {
            "group_id": group.id,
            "child_id": group.child_id,
            "members": [
                {"user_id": m.user_id, "relation": m.relation, "joined_at": m.created_at}
                for m in members
            ],
        }

    async def add_member(
        self,
        group_id: str,
        user_id: str,
        relation: str,
        actor_user_id: str,
    ) -> Dict[str, Any]:
        group_stmt = select(FamilyGroup).where(FamilyGroup.id == group_id)
        group = (await self.db.execute(group_stmt)).scalar_one_or_none()
        if not group:
            raise ValueError("家庭组不存在")

        existing_stmt = select(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        )
        existing = (await self.db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            return {"member": {"user_id": existing.user_id, "relation": existing.relation}}

        member = GroupMember(
            id=str(uuid.uuid4()),
            group_id=group_id,
            user_id=user_id,
            relation=relation,
        )
        self.db.add(member)

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=group.child_id,
            actor_user_id=actor_user_id,
            action="member_added",
            entity_type="group_member",
            entity_id=member.id,
            level=2,
            changes_json=json.dumps({"relation": relation, "user_id": user_id}),
        )
        self.db.add(audit)
        await self.db.commit()

        return {"member": {"user_id": user_id, "relation": relation}}

    async def remove_member(
        self, group_id: str, member_user_id: str, actor_user_id: str
    ) -> Dict[str, Any]:
        group_stmt = select(FamilyGroup).where(FamilyGroup.id == group_id)
        group = (await self.db.execute(group_stmt)).scalar_one_or_none()
        if not group:
            raise ValueError("家庭组不存在")

        member_stmt = select(GroupMember).where(
            and_(GroupMember.group_id == group_id, GroupMember.user_id == member_user_id)
        )
        member = (await self.db.execute(member_stmt)).scalar_one_or_none()
        if not member:
            raise ValueError("成员不存在")

        # 删除（软删除）
        member.status = "removed"

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=group.child_id,
            actor_user_id=actor_user_id,
            action="member_removed",
            entity_type="group_member",
            entity_id=member.id,
            level=2,
        )
        self.db.add(audit)
        await self.db.commit()

        return {"removed": True, "member_id": member.id}

    async def create_consent(
        self,
        actor_user_id: str,
        child_id: str,
        scope: str,
        purpose: str,
        source: str,
    ) -> Dict[str, Any]:
        consent = Consent(
            id=str(uuid.uuid4()),
            child_id=child_id,
            actor_user_id=actor_user_id,
            scope=scope,
            purpose=purpose,
            source=source,
            status="active",
        )
        self.db.add(consent)
        await self.db.commit()

        return {
            "id": consent.id,
            "child_id": child_id,
            "scope": scope,
            "purpose": purpose,
            "status": "active",
            "source": source,
        }

    async def revoke_consent(
        self, actor_user_id: str, consent_id: str
    ) -> Dict[str, Any]:
        consent_stmt = select(Consent).where(Consent.id == consent_id)
        consent = (await self.db.execute(consent_stmt)).scalar_one_or_none()
        if not consent:
            raise ValueError("授权不存在")

        # 权限校验：只有创建该授权的用户或该孩子的 child_profile 所属用户才能撤销
        child_stmt = select(ChildProfile).where(ChildProfile.id == consent.child_id)
        child = (await self.db.execute(child_stmt)).scalar_one_or_none()
        if not child:
            raise ValueError("孩子档案不存在")
        if consent.actor_user_id != actor_user_id and child.user_id != actor_user_id:
            raise PermissionError("无权撤销此授权")

        consent.status = "revoked"

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=consent.child_id,
            actor_user_id=actor_user_id,
            action="consent_revoked",
            entity_type="consent",
            entity_id=consent_id,
            level=consent.level,
        )
        self.db.add(audit)
        await self.db.commit()

        return {"revoked": True, "consent_id": consent_id, "affected_shares": []}
