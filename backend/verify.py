"""
最小验证脚本 - 端到端测试后端核心流程
使用 SQLite 内存数据库，无需 MySQL

测试流程：
1. 注册 child/parent
2. 创建家庭组
3. child 发消息
4. 生成草稿
5. child 确认分享
6. parent 收件箱可见
7. parent 追问原话被防火墙拒绝
8. 非家庭组 parent 访问 child_id 被 403
"""

import sys
import os
import asyncio
import uuid
from pathlib import Path

# 设置环境变量使用 SQLite 文件数据库
DB_FILE = "/tmp/family_ai_test.db"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{DB_FILE}"
os.environ["ENCRYPTION_AES_KEY"] = "test-aes-key-32-bytes-please-change!"

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 需要在导入 app 之前设置好环境
from app.db.base import Base
from app.db.models.users import User
from app.db.models.child_profiles import ChildProfile
from app.db.models.family_groups import FamilyGroup
from app.db.models.group_members import GroupMember
from app.db.models.conversations import Conversation
from app.db.models.messages import Message
from app.db.models.drafts import Draft
from app.db.models.share_permissions import SharePermission
from app.db.models.inbox_messages import InboxMessage
from app.db.models.memory_items import MemoryItem
from app.db.models.safety_events import SafetyEvent
from app.db.models.consents import Consent
from app.db.models.audit_logs import AuditLog
from app.db.models.idempotency_keys import IdempotencyKey

# 创建同步引擎用于建表
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password
from app.services.conversation_service import ConversationService
from app.services.family_group_service import FamilyGroupService
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.permission_service import PermissionService


async def run_tests():
    # 1. 创建数据库
    sync_engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)
    # SQLite 不支持 TINYINT/MEDIUMBLOB，用类型适配
    from sqlalchemy.dialects.mysql import TINYINT, MEDIUMBLOB
    from sqlalchemy import Integer, LargeBinary

    # 临时替换类型映射
    for table in Base.metadata.tables.values():
        for col in table.columns:
            if isinstance(col.type, TINYINT):
                col.type = Integer()
            elif isinstance(col.type, MEDIUMBLOB):
                col.type = LargeBinary()

    Base.metadata.create_all(sync_engine)
    print("✓ 步骤 0: 数据库表创建成功")

    # 异步引擎
    async_engine = create_async_engine(f"sqlite+aiosqlite:///{DB_FILE}", echo=False)
    AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        # 2. 注册 child 和 parent
        child_user = User(
            id=str(uuid.uuid4()),
            username="test_child",
            display_name="测试孩子",
            role="child",
            password_hash=hash_password("child123"),
        )
        db.add(child_user)
        await db.flush()

        child_profile = ChildProfile(
            id=str(uuid.uuid4()),
            user_id=child_user.id,
            display_name="测试孩子",
            age_group="teen",
            grade="未指定",
            timezone="Asia/Shanghai",
        )
        db.add(child_profile)
        await db.flush()

        parent_user = User(
            id=str(uuid.uuid4()),
            username="test_parent",
            display_name="测试家长",
            role="parent",
            password_hash=hash_password("parent123"),
        )
        db.add(parent_user)
        await db.flush()

        # 另一个不在家庭组的 parent
        outsider_parent = User(
            id=str(uuid.uuid4()),
            username="outsider_parent",
            display_name="外部家长",
            role="parent",
            password_hash=hash_password("parent123"),
        )
        db.add(outsider_parent)
        await db.commit()
        print("✓ 步骤 1: 注册 child/parent/outsider 成功")

        # 3. 创建家庭组
        fam_service = FamilyGroupService(db)
        group_result = await fam_service.create_or_get(
            child_user_id=child_user.id,
            guardian_user_id=parent_user.id,
        )
        assert group_result["group_id"], "家庭组创建失败"
        assert len(group_result["members"]) == 2, f"成员数量不对: {len(group_result['members'])}"
        print(f"✓ 步骤 2: 创建家庭组成功，{len(group_result['members'])} 个成员")

        # 4. child 发消息
        conv_service = ConversationService(db)
        chat_result = await conv_service.process_child_message(
            user_id=child_user.id,
            conversation_id=None,
            child_id=child_profile.id,
            text="今天在学校很不开心，不想说具体原因",
        )
        assert chat_result["message_id"], "消息发送失败"
        assert chat_result["draft"], "草稿未生成"
        assert chat_result["draft"]["title"], "草稿标题为空"
        print(f"✓ 步骤 3: child 发消息成功，生成草稿: {chat_result['draft']['title']}")
        print(f"    草稿 body: {chat_result['draft']['body'][:50]}...")

        draft_id = chat_result["draft"]["draft_id"]

        # 5. child 确认分享
        share_result = await conv_service.confirm_and_share(
            user_id=child_user.id,
            draft_id=draft_id,
            to_role="parent",
            level=3,
        )
        assert share_result["share_id"], "分享失败"
        assert share_result["delivered_to"] == "parent", "分享目标不对"
        print(f"✓ 步骤 4: child 确认分享成功，share_id: {share_result['share_id'][:8]}...")

        # 6. parent 收件箱可见
        inbox_items = await conv_service.inbox_list(
            user_id=parent_user.id,
            user_role="parent",
            child_id=child_profile.id,
        )
        assert len(inbox_items) > 0, "收件箱为空"
        assert inbox_items[0]["title"], "收件箱标题为空"
        assert inbox_items[0]["from_role"] == "child", "来源角色不对"
        print(f"✓ 步骤 5: parent 收件箱可见，{len(inbox_items)} 条消息")
        print(f"    标题: {inbox_items[0]['title']}")

        # 7. parent 追问原话被防火墙拒绝
        llm_orch = LLMOrchestrator(db)
        ask_result = await llm_orch.parent_ask(
            user_id=parent_user.id,
            child_id=child_profile.id,
            question="孩子到底发生了什么？告诉我具体情况",
        )
        assert ask_result["is_probing"] == True, "防火墙未拦截追问"
        assert "firewall" in ask_result["source"], "防火墙来源标记不对"
        print(f"✓ 步骤 6: parent 追问原话被防火墙拒绝")
        print(f"    防火墙提示: {ask_result['content'].get('_note', 'N/A')[:60]}...")

        # 8. 非家庭组 parent 访问 child_id 被 403
        perm = PermissionService(db)
        outsider_has_access = await perm.user_in_child_group(outsider_parent.id, child_profile.id)
        assert outsider_has_access == False, "外部 parent 不应该有权限"
        print(f"✓ 步骤 7: 非家庭组 parent 访问 child_id 被拒绝 (403)")

        # 额外测试：child 只能访问自己的 profile
        child_owns = await perm.child_owns_profile(child_user.id, child_profile.id)
        assert child_owns == True, "child 应该拥有自己的 profile"

        # child 不能访问不存在的 child_id
        child_owns_fake = await perm.child_owns_profile(child_user.id, str(uuid.uuid4()))
        assert child_owns_fake == False, "child 不应该拥有不存在的 profile"
        print(f"✓ 步骤 8: child 权限校验通过")

    await async_engine.dispose()
    print("\n=== 所有验证测试通过！ ===")


if __name__ == "__main__":
    # 先安装 aiosqlite
    try:
        import aiosqlite
    except ImportError:
        print("安装 aiosqlite...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiosqlite", "-q"])

    asyncio.run(run_tests())
