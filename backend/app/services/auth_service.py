"""
用户和认证服务
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.users import User
from app.db.models.child_profiles import ChildProfile
from app.core.security import verify_password, hash_password, create_jwt, decode_jwt
from app.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(
        self, username: str, display_name: str, role: str, password: str
    ) -> Dict[str, Any]:
        stmt = select(User).where(User.username == username)
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise ValueError("用户名已存在")

        user = User(
            id=str(uuid.uuid4()),
            username=username,
            display_name=display_name,
            role=role,
            password_hash=hash_password(password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        profile = None
        if role == "child":
            profile = ChildProfile(
                id=str(uuid.uuid4()),
                user_id=user.id,
                display_name=display_name,
                age_group="unspecified",
                grade="未指定",
                timezone="Asia/Shanghai",
            )
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)

        tokens = create_jwt(user.id, user.role)
        result = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
        }
        if profile:
            result["child_profile_id"] = profile.id
        return result

    async def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        stmt = select(User).where(User.username == username)
        user = (await self.db.execute(stmt)).scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            return None

        tokens = create_jwt(user.id, user.role)
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
        }

    async def get_me(self, user_id: str) -> Dict[str, Any]:
        stmt = select(User).where(User.id == user_id)
        user = (await self.db.execute(stmt)).scalar_one_or_none()
        if not user:
            raise ValueError("用户不存在")

        profiles_stmt = select(ChildProfile).where(ChildProfile.user_id == user_id)
        profiles = (await self.db.execute(profiles_stmt)).scalars().all()

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "role": user.role,
            },
            "child_profiles": [
                {
                    "id": p.id,
                    "display_name": p.display_name,
                    "age_group": p.age_group,
                    "grade": p.grade,
                }
                for p in profiles
            ],
        }

    async def find_user_by_id(self, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()
