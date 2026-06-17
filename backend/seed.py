"""
种子数据脚本 - 创建演示账号
使用 ORM 方式插入，避免字段不匹配
"""

import sys
import uuid
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db.base import Base
from app.db.models.users import User
from app.db.models.child_profiles import ChildProfile
from app.db.models.family_groups import FamilyGroup
from app.db.models.group_members import GroupMember
from app.core.security import hash_password


def get_sync_engine():
    url = settings.DATABASE_URL
    if url.startswith("mysql+aiomysql://"):
        url = url.replace("mysql+aiomysql://", "mysql+pymysql://", 1)
    return create_engine(url, echo=False)


def seed():
    engine = get_sync_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    # 确保表存在
    Base.metadata.create_all(engine)

    users_data = [
        ("kid_demo", "小明（孩子）", "child", "child123"),
        ("parent_demo", "妈妈（家长）", "parent", "parent123"),
        ("teacher_demo", "班主任（老师）", "teacher", "teacher123"),
    ]

    child_user_id = None
    parent_user_id = None
    teacher_user_id = None

    for username, display_name, role, password in users_data:
        existing = session.query(User).filter(User.username == username).first()
        if not existing:
            user = User(
                id=str(uuid.uuid4()),
                username=username,
                display_name=display_name,
                role=role,
                password_hash=hash_password(password),
            )
            session.add(user)
            session.flush()
            uid = user.id
            print(f"[OK] 创建用户: {username} / {password}")
        else:
            uid = existing.id
            print(f"[SKIP] 用户已存在: {username}")

        if role == "child":
            child_user_id = uid
        elif role == "parent":
            parent_user_id = uid
        elif role == "teacher":
            teacher_user_id = uid

    # 创建孩子档案
    child_id = None
    if child_user_id:
        existing_child = session.query(ChildProfile).filter(
            ChildProfile.user_id == child_user_id
        ).first()

        if not existing_child:
            child = ChildProfile(
                id=str(uuid.uuid4()),
                user_id=child_user_id,
                display_name="小明",
                age_group="teen",
                grade="未指定",
                timezone="Asia/Shanghai",
            )
            session.add(child)
            session.flush()
            child_id = child.id
            print(f"[OK] 创建孩子档案: {child_id}")
        else:
            child_id = existing_child.id
            print(f"[SKIP] 孩子档案已存在: {child_id}")

    # 创建家庭组
    if child_id and parent_user_id:
        existing_group = session.query(FamilyGroup).filter(
            FamilyGroup.child_id == child_id
        ).first()

        if not existing_group:
            group = FamilyGroup(
                id=str(uuid.uuid4()),
                child_id=child_id,
                name="小明的家庭组",
            )
            session.add(group)
            session.flush()

            # 添加孩子自己
            session.add(GroupMember(
                id=str(uuid.uuid4()),
                group_id=group.id,
                user_id=child_user_id,
                relation="self",
            ))
            # 添加家长
            session.add(GroupMember(
                id=str(uuid.uuid4()),
                group_id=group.id,
                user_id=parent_user_id,
                relation="guardian",
            ))
            # 添加老师
            if teacher_user_id:
                session.add(GroupMember(
                    id=str(uuid.uuid4()),
                    group_id=group.id,
                    user_id=teacher_user_id,
                    relation="teacher",
                ))
            print(f"[OK] 创建家庭组: {group.id}")

    session.commit()
    session.close()
    engine.dispose()
    print("\n=== 种子数据创建完成 ===")
    print("可用账号：")
    for username, display_name, role, password in users_data:
        print(f"  - {username} / {password} ({display_name})")


if __name__ == "__main__":
    seed()
