"""
权限校验服务
统一校验用户与孩子的关系：
- child 只能访问自己的 child_profile
- parent/teacher/counselor 只能访问同一家庭组/授权关系下的 child_id
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.child_profiles import ChildProfile
from app.db.models.family_groups import FamilyGroup
from app.db.models.group_members import GroupMember


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def child_owns_profile(self, user_id: str, child_id: str) -> bool:
        """校验孩子用户是否拥有该 child_profile"""
        stmt = select(ChildProfile).where(
            and_(ChildProfile.id == child_id, ChildProfile.user_id == user_id)
        )
        result = (await self.db.execute(stmt)).scalar_one_or_none()
        return result is not None

    async def user_in_child_group(self, user_id: str, child_id: str) -> bool:
        """校验用户是否在孩子所属家庭组的活跃成员中"""
        # 先找到孩子所属的家庭组
        group_stmt = select(FamilyGroup).where(FamilyGroup.child_id == child_id)
        group = (await self.db.execute(group_stmt)).scalar_one_or_none()
        if not group:
            return False

        # 查询用户是否是该家庭组的活跃成员
        member_stmt = select(GroupMember).where(
            and_(
                GroupMember.group_id == group.id,
                GroupMember.user_id == user_id,
                GroupMember.status == "active",
            )
        )
        member = (await self.db.execute(member_stmt)).scalar_one_or_none()
        return member is not None

    async def user_can_access_child(
        self, user_id: str, role: str, child_id: str
    ) -> bool:
        """综合权限校验：
        - child: 只能访问自己的 profile
        - parent/teacher/counselor: 必须在同一家庭组
        """
        if role == "child":
            return await self.child_owns_profile(user_id, child_id)
        # guardian 角色（parent/teacher/counselor）
        return await self.user_in_child_group(user_id, child_id)

    async def get_accessible_child_ids(self, user_id: str, role: str) -> List[str]:
        """获取用户可以访问的所有 child_id 列表"""
        if role == "child":
            # child 只能访问自己的 profile
            stmt = select(ChildProfile).where(ChildProfile.user_id == user_id)
            profiles = (await self.db.execute(stmt)).scalars().all()
            return [p.id for p in profiles]

        # guardian：查询其所在的所有家庭组的孩子
        # 先找用户所在的所有活跃 group_id
        member_stmt = select(GroupMember.group_id).where(
            and_(
                GroupMember.user_id == user_id,
                GroupMember.status == "active",
            )
        )
        group_ids = [row[0] for row in (await self.db.execute(member_stmt)).all()]
        if not group_ids:
            return []

        # 再查这些 group 的 child_id
        group_stmt = select(FamilyGroup.child_id).where(
            FamilyGroup.id.in_(group_ids)
        )
        child_ids = [row[0] for row in (await self.db.execute(group_stmt)).all()]
        return child_ids

    async def verify_child_access_or_raise(
        self, user_id: str, role: str, child_id: str
    ) -> None:
        """校验权限，失败抛出 PermissionError"""
        if not await self.user_can_access_child(user_id, role, child_id):
            raise PermissionError("无权访问该孩子档案")
