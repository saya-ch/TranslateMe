"""
种子数据脚本 - 创建演示账号
"""

import sys
import uuid
import asyncio
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
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

    users = [
        {
            "id": str(uuid.uuid4()),
            "username": "kid_demo",
            "display_name": "小明（孩子）",
            "role": "child",
            "password": "child123",
        },
        {
            "id": str(uuid.uuid4()),
            "username": "parent_demo",
            "display_name": "妈妈（家长）",
            "role": "parent",
            "password": "parent123",
        },
        {
            "id": str(uuid.uuid4()),
            "username": "teacher_demo",
            "display_name": "班主任（老师）",
            "role": "teacher",
            "password": "teacher123",
        },
    ]

    # 插入用户
    child_user_id = None
    parent_user_id = None
    for u in users:
        existing = session.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": u["username"]},
        ).fetchone()

        if not existing:
            session.execute(
                text(
                    "INSERT INTO users (id, username, display_name, role, password_hash, created_at) "
                    "VALUES (:id, :username, :display_name, :role, :password_hash, NOW())"
                ),
                {
                    "id": u["id"],
                    "username": u["username"],
                    "display_name": u["display_name"],
                    "role": u["role"],
                    "password_hash": hash_password(u["password"]),
                },
            )
            print(f"[OK] 创建用户: {u['username']} / {u['password']}")
        else:
            u["id"] = existing[0]
            print(f"[SKIP] 用户已存在: {u['username']}")

        if u["role"] == "child":
            child_user_id = u["id"]
        if u["role"] == "parent":
            parent_user_id = u["id"]

    # 创建孩子档案
    child_id = None
    if child_user_id:
        existing_child = session.execute(
            text("SELECT id FROM child_profiles WHERE user_id = :user_id"),
            {"user_id": child_user_id},
        ).fetchone()

        if not existing_child:
            child_id = str(uuid.uuid4())
            session.execute(
                text(
                    "INSERT INTO child_profiles (id, user_id, display_name, age_group, grade, timezone, created_at) "
                    "VALUES (:id, :user_id, :display_name, :age_group, :grade, :timezone, NOW())"
                ),
                {
                    "id": child_id,
                    "user_id": child_user_id,
                    "display_name": "小明",
                    "age_group": "teen",
                    "grade": "未指定",
                    "timezone": "Asia/Shanghai",
                },
            )
            print(f"[OK] 创建孩子档案: {child_id}")
        else:
            child_id = existing_child[0]

    # 创建家庭组
    if child_id and parent_user_id:
        existing_group = session.execute(
            text("SELECT id FROM family_groups WHERE child_id = :child_id"),
            {"child_id": child_id},
        ).fetchone()

        if not existing_group:
            group_id = str(uuid.uuid4())
            session.execute(
                text(
                    "INSERT INTO family_groups (id, child_id, name, created_at) "
                    "VALUES (:id, :child_id, :name, NOW())"
                ),
                {"id": group_id, "child_id": child_id, "name": "小明的家庭组"},
            )

            # 添加成员
            for idx, member_user_id in enumerate([child_user_id, parent_user_id]):
                relation = "self" if idx == 0 else "guardian"
                session.execute(
                    text(
                        "INSERT INTO group_members (id, group_id, user_id, relation, created_at) "
                        "VALUES (:id, :group_id, :user_id, :relation, NOW())"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "group_id": group_id,
                        "user_id": member_user_id,
                        "relation": relation,
                    },
                )
            print(f"[OK] 创建家庭组: {group_id}")

    session.commit()
    session.close()
    engine.dispose()
    print("\n=== 种子数据创建完成 ===")
    print("可用账号：")
    for u in users:
        print(f"  - {u['username']} / {u['password']} ({u['display_name']})")


if __name__ == "__main__":
    seed()
