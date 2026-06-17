"""
权限校验服务 - 校验用户与孩子的关系
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.users import User
from app.db.models.child_profiles import ChildProfile
from app.db.models.family_groups import FamilyGroup
from app.db.models.group_members import GroupMember


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_child_profile_by_user_id(self, user_id: str) -> Optional[ChildProfile]:
        """通过 user_id 获取孩子的 child_profile（仅 role=child）"""
        stmt = select(ChildProfile).where(ChildProfile.user_id == user_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_child_profile(self, child_id: str) -> Optional[ChildProfile]:
        stmt = select(ChildProfile).where(ChildProfile.id == child_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def child_owns_profile(self, user_id: str, child_id: str) -> bool:
        """校验孩子用户是否拥有该 child_profile"""
        stmt = select(ChildProfile).where(
            and_(ChildProfile.id == child_id, ChildProfile.user_id == user_id)
        )
        result = (await self.db.execute(stmt)).scalar_one_or_none()
        return result is not None

    async def user_in_child_group(self, user_id: str, child_id: str) -> bool:
        """校验用户是否在孩子所属家庭组的活跃成员中"""
        # 找到孩子的家庭组
        group_stmt = select(FamilyGroup).where(FamilyGroup.child_id == child_id)
        group = (await self.db.execute(group_stmt)).scalar_one_or_none()
        if not group:
            return False

        # 检查是否是活跃成员
        member_stmt = select(GroupMember).where(
            and_(
                GroupMember.group_id == group.id,
                GroupMember.user_id == user_id,
                GroupMember.status == "active",
            )
        )
        member = (await self.db.execute(member_stmt)).scalar_one_or_none()
        return member is not None

    async def user_can_access_child(self, user_id: str, role: str, child_id: str) -> bool:
        """综合权限校验：用户是否能访问该孩子"""
        if role == "child":
            return await self.child_owns_profile(user_id, child_id)
        else:
            # parent/teacher/counselor 必须在同一家庭组
            return await self.user_in_child_group(user_id, child_id)

    async def get_accessible_child_ids(self, user_id: str, role: str) -> List[str]:
        """获取用户可以访问的所有 child_id 列表"""
        if role == "child":
            profile = await self.get_child_profile_by_user_id(user_id)
            return [profile.id] if profile else []
        else:
            # 查找用户所在的所有家庭组
            stmt = (
                select(FamilyGroup.child_id)
                .join(GroupMember, GroupMember.group_id == FamilyGroup.id)
                .where(
                    and_(
                        GroupMember.user_id == user_id,
                        GroupMember.status == "active",
                    )
                )
            )
            result = await self.db.execute(stmt)
            return [row[0] for row in result.fetchall()]
