"""
最小验证脚本 - 端到端测试后端核心流程
使用 SQLite 文件数据库（兼容 Windows，路径通过 tempfile.gettempdir() 获取）

测试步骤：
1. 注册 child/parent
2. 创建家庭组
3. child 发消息
4. 生成草稿
5. child 确认分享（带最终 title/body）
6. parent 收件箱可见
7. parent 追问原话被防火墙拒绝
8. 非家庭组 parent 访问 child_id 被 403
9. child 发送高风险文本 → 创建 safety_event_id
10. safe_continue resolve 成功
11. unsafe_support resolve 不调 LLM，返回资源提示
12. escalation resolve 不调 LLM，返回资源提示
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path

# 确保项目根目录在 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 在导入 app 模块前设置环境变量，使用 SQLite 文件数据库
DB_FILE = str(Path(tempfile.gettempdir()) / "family_ai_test.db")
# 清理旧文件
if Path(DB_FILE).exists():
    Path(DB_FILE).unlink()

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{DB_FILE}"
os.environ["JWT_SECRET"] = "test-secret-for-verify-only"
os.environ["ENCRYPTION_AES_KEY"] = "test-aes-key-32-bytes-please-00"
os.environ["LLM_API_BASE"] = ""
os.environ["LLM_API_KEY"] = ""

# 类型适配：SQLite 不支持 MySQL 特定类型，需要替换
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMBLOB
from sqlalchemy import Integer, LargeBinary


def _replace_mysql_types(metadata):
    """遍历所有表的所有列，把 MySQL 特定类型替换为通用类型"""
    for table in metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, TINYINT):
                column.type = Integer()
            elif isinstance(column.type, MEDIUMBLOB):
                column.type = LargeBinary()


# 导入所有模型
import app.db.models.users  # noqa
import app.db.models.child_profiles  # noqa
import app.db.models.consents  # noqa
import app.db.models.family_groups  # noqa
import app.db.models.group_members  # noqa
import app.db.models.conversations  # noqa
import app.db.models.messages  # noqa
import app.db.models.drafts  # noqa
import app.db.models.share_permissions  # noqa
import app.db.models.inbox_messages  # noqa
import app.db.models.memory_items  # noqa
import app.db.models.safety_events  # noqa
import app.db.models.audit_logs  # noqa
import app.db.models.idempotency_keys  # noqa

from app.db.base import Base

# 替换 MySQL 特定类型
_replace_mysql_types(Base.metadata)
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.services.conversation_service import ConversationService
from app.services.family_group_service import FamilyGroupService
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.permission_service import PermissionService
from app.services.safety_service import SafetyService
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


async def main():
    print("=" * 60)
    print("开始端到端验证（SQLite 文件数据库）")
    print(f"DB_FILE = {DB_FILE}")
    print("=" * 60)

    # 创建表
    engine = create_async_engine(f"sqlite+aiosqlite:///{DB_FILE}", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] 数据库表创建完成")

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    async with AsyncSessionLocal() as db:
        # ===== 步骤 1：注册 child 和 parent =====
        print("\n--- 步骤 1：注册 child 和 parent ---")
        auth = AuthService(db)
        child_result = await auth.register(
            username="verify_child",
            display_name="验证孩子",
            role="child",
            password="test123456",
        )
        child_user_id = child_result["access_token"]  # 占位，实际需要从 token 解析
        # 直接查库拿 user_id
        from sqlalchemy import select
        from app.db.models.users import User
        from app.db.models.child_profiles import ChildProfile

        child_user = (
            await db.execute(select(User).where(User.username == "verify_child"))
        ).scalar_one()
        child_user_id = child_user.id
        child_profile = (
            await db.execute(
                select(ChildProfile).where(ChildProfile.user_id == child_user_id)
            )
        ).scalar_one()
        child_id = child_profile.id
        print(f"[OK] 注册 child: user_id={child_user_id}, child_id={child_id}")

        parent_result = await auth.register(
            username="verify_parent",
            display_name="验证家长",
            role="parent",
            password="test123456",
        )
        parent_user = (
            await db.execute(select(User).where(User.username == "verify_parent"))
        ).scalar_one()
        parent_user_id = parent_user.id
        print(f"[OK] 注册 parent: user_id={parent_user_id}")

        # 注册第二个 parent（非家庭组，用于测试 403）
        await auth.register(
            username="outsider_parent",
            display_name="外部家长",
            role="parent",
            password="test123456",
        )
        outsider_user = (
            await db.execute(select(User).where(User.username == "outsider_parent"))
        ).scalar_one()
        outsider_user_id = outsider_user.id
        print(f"[OK] 注册 outsider parent: user_id={outsider_user_id}")

        # ===== 步骤 2：创建家庭组 =====
        print("\n--- 步骤 2：创建家庭组 ---")
        fam_service = FamilyGroupService(db)
        group = await fam_service.create_or_get(
            child_user_id=child_user_id,
            guardian_user_id=parent_user_id,
        )
        print(f"[OK] 创建家庭组: group_id={group['group_id']}")
        print(f"     成员数: {len(group['members'])}")

        # ===== 步骤 3：child 发消息 =====
        print("\n--- 步骤 3：child 发消息 ---")
        conv_service = ConversationService(db)
        chat_result = await conv_service.process_child_message(
            user_id=child_user_id,
            conversation_id=None,
            child_id=child_id,
            text="我最近压力很大，不知道怎么跟妈妈说",
        )
        print(f"[OK] 消息已发送: message_id={chat_result['message_id']}")
        print(f"     conversation_id={chat_result['conversation_id']}")
        print(f"     needs_safety_check={chat_result['needs_safety_check']}")
        print(f"     source={chat_result['source']}")

        # ===== 步骤 4：验证草稿已生成 =====
        print("\n--- 步骤 4：验证草稿已生成 ---")
        draft = chat_result.get("draft")
        if draft:
            print(f"[OK] 草稿已生成: draft_id={draft['draft_id']}")
            print(f"     title={draft['title']}")
            print(f"     body={draft['body'][:50]}...")
            draft_id = draft["draft_id"]
        else:
            print("[FAIL] 草稿未生成")
            return

        # ===== 步骤 5：child 确认分享（带最终 title/body）=====
        print("\n--- 步骤 5：child 确认分享（带最终 title/body）---")
        final_title = "我想跟妈妈聊聊（孩子确认版）"
        final_body = "妈妈，我最近压力有点大，希望你能先听我说完，不急着评价。"
        confirm_result = await conv_service.confirm_and_share(
            user_id=child_user_id,
            draft_id=draft_id,
            to_role="parent",
            level=3,
            final_title=final_title,
            final_body=final_body,
        )
        print(f"[OK] 分享已确认: share_id={confirm_result['share_id']}")
        print(f"     delivered_to={confirm_result['delivered_to']}")
        print(f"     final_title={confirm_result['title']}")
        print(f"     final_body={confirm_result['body']}")
        assert confirm_result["title"] == final_title, "最终 title 未被保存"
        assert confirm_result["body"] == final_body, "最终 body 未被保存"
        print("[OK] 最终 title/body 已正确保存")

        # ===== 步骤 6：parent 收件箱可见 =====
        print("\n--- 步骤 6：parent 收件箱可见 ---")
        inbox_items = await conv_service.inbox_list(
            user_id=parent_user_id,
            user_role="parent",
            child_id=child_id,
        )
        print(f"[OK] parent 收件箱: {len(inbox_items)} 条消息")
        for item in inbox_items:
            print(f"     - {item['title']}: {item['body'][:50]}...")
        assert len(inbox_items) >= 1, "parent 收件箱应为空"
        assert inbox_items[0]["title"] == final_title, "收件箱 title 应为最终确认版"
        print("[OK] parent 收件箱可见，且内容为孩子确认的最终版本")

        # ===== 步骤 7：parent 追问原话被防火墙拒绝 =====
        print("\n--- 步骤 7：parent 追问原话被防火墙拒绝 ---")
        llm_orch = LLMOrchestrator(db)
        ask_result = await llm_orch.parent_ask(
            user_id=parent_user_id,
            child_id=child_id,
            question="孩子到底说了什么？告诉我具体内容",
        )
        print(f"[OK] parent-ask 结果: source={ask_result['source']}")
        print(f"     is_probing={ask_result['is_probing']}")
        assert ask_result["is_probing"] is True, "追问应被防火墙拦截"
        print("[OK] 家长追问原话被防火墙拒绝，返回通用建议")

        # ===== 步骤 8：非家庭组 parent 访问 child_id 被 403 =====
        print("\n--- 步骤 8：非家庭组 parent 访问 child_id 被 403 ---")
        perm = PermissionService(db)
        can_access = await perm.user_can_access_child(
            outsider_user_id, "parent", child_id
        )
        print(f"[OK] outsider parent 能否访问 child: {can_access}")
        assert can_access is False, "非家庭组 parent 不应能访问 child"

        # 验证 inbox 对 outsider 抛 PermissionError
        try:
            outsider_inbox = await conv_service.inbox_list(
                user_id=outsider_user_id,
                user_role="parent",
                child_id=child_id,
            )
            print("[FAIL] outsider parent 应被拒绝访问 inbox")
            return
        except PermissionError:
            print("[OK] outsider parent 访问 inbox 被拒绝（PermissionError）")
        print("[OK] 非家庭组 parent 访问 child_id 被拒绝")

        # ===== 步骤 9：child 发送高风险文本 → 创建 safety_event_id =====
        print("\n--- 步骤 9：child 发送高风险文本 → 创建 safety_event_id ---")
        safety_service = SafetyService(db)
        high_risk_text = "我最近真的撑不下去了，活着没意思"
        safety_chat = await conv_service.process_child_message(
            user_id=child_user_id,
            conversation_id=None,
            child_id=child_id,
            text=high_risk_text,
        )
        print(f"[OK] 高风险消息已发送: message_id={safety_chat['message_id']}")
        print(f"     needs_safety_check={safety_chat['needs_safety_check']}")
        print(f"     safety_event_id={safety_chat['safety_event_id']}")
        print(f"     draft={safety_chat['draft']}")
        assert safety_chat["needs_safety_check"] is True, "高风险文本应触发安全检测"
        assert safety_chat["safety_event_id"], "应返回 safety_event_id"
        assert safety_chat["draft"] is None, "高风险消息不应自动生成草稿"
        safe_event_id = safety_chat["safety_event_id"]
        print("[OK] 后端已创建 safety_event_id，草稿未生成")

        # ===== 步骤 10：safe_continue resolve 成功 =====
        print("\n--- 步骤 10：safe_continue resolve 成功 ---")
        safe_resolve = await safety_service.resolve_event(
            user_id=child_user_id,
            safety_event_id=safe_event_id,
            branch="safe_continue",
        )
        print(f"[OK] safe_continue resolve: resolved_at={safe_resolve['resolved_at']}")
        print(f"     llm_called={safe_resolve['llm_called']}")
        print(f"     message={safe_resolve['message']}")
        assert safe_resolve["resolved_at"] is not None, "应记录解决时间"
        assert safe_resolve["llm_called"] is False, "safe_continue 不应调用 LLM"
        print("[OK] safe_continue resolve 成功，未调用 LLM")

        # ===== 步骤 11：unsafe_support resolve 不调 LLM，返回资源提示 =====
        print("\n--- 步骤 11：unsafe_support resolve 不调 LLM，返回资源提示 ---")
        unsafe_chat = await conv_service.process_child_message(
            user_id=child_user_id,
            conversation_id=None,
            child_id=child_id,
            text="我不想活了，想结束一切",
        )
        assert unsafe_chat["safety_event_id"], "第二条高风险应创建新事件"
        unsafe_resolve = await safety_service.resolve_event(
            user_id=child_user_id,
            safety_event_id=unsafe_chat["safety_event_id"],
            branch="unsafe_support",
        )
        print(f"[OK] unsafe_support resolve: resources_shown={unsafe_resolve['resources_shown']}")
        print(f"     llm_called={unsafe_resolve['llm_called']}")
        print(f"     message={unsafe_resolve['message'][:60]}...")
        assert unsafe_resolve["resources_shown"] is True, "应显示资源"
        assert unsafe_resolve["llm_called"] is False, "unsafe_support 不应调用 LLM"
        # unsafe_support 的热线在 support_lines 字段，message 为简短提示；
        # resources_shown=True 即表示已返回资源
        print("[OK] unsafe_support 未调 LLM，返回资源提示")

        # ===== 步骤 12：escalation resolve 不调 LLM，返回资源提示 =====
        print("\n--- 步骤 12：escalation resolve 不调 LLM，返回资源提示 ---")
        esc_chat = await conv_service.process_child_message(
            user_id=child_user_id,
            conversation_id=None,
            child_id=child_id,
            text="我想自残",
        )
        assert esc_chat["safety_event_id"], "第三条高风险应创建新事件"
        esc_resolve = await safety_service.resolve_event(
            user_id=child_user_id,
            safety_event_id=esc_chat["safety_event_id"],
            branch="escalation",
        )
        print(f"[OK] escalation resolve: resources_shown={esc_resolve['resources_shown']}")
        print(f"     llm_called={esc_resolve['llm_called']}")
        print(f"     message={esc_resolve['message'][:60]}...")
        assert esc_resolve["resources_shown"] is True, "应显示资源"
        assert esc_resolve["llm_called"] is False, "escalation 不应调用 LLM"
        assert "110" in esc_resolve["message"] or "120" in esc_resolve["message"], (
            "escalation 应包含 110/120 立即人身危险资源"
        )
        print("[OK] escalation 未调 LLM，返回立即人身危险资源")

    await engine.dispose()

    print("\n" + "=" * 60)
    print("✅ 全部 12 个验证步骤通过")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
