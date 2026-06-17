"""
核心会话服务：孩子输入消息 → 安全检测 → 记忆提取 → 草稿生成 → 用户确认 → 分享
"""

import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.conversations import Conversation
from app.db.models.messages import Message
from app.db.models.drafts import Draft
from app.db.models.share_permissions import SharePermission
from app.db.models.inbox_messages import InboxMessage
from app.db.models.memory_items import MemoryItem
from app.db.models.safety_events import SafetyEvent
from app.db.models.audit_logs import AuditLog
from app.db.models.child_profiles import ChildProfile
from app.core.security import aes_encrypt, aes_decrypt
from app.core.safety_patterns import needs_safety_check, detect_patterns, text_hash
from app.core.llm_client import llm_client
from app.core.llm_prompts import DRAFT_SYSTEM_PROMPT
from app.core.llm_fallback import generate_draft_fallback
from app.config import settings


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== 主入口：孩子发送消息 ==========
    async def process_child_message(
        self, user_id: str, conversation_id: Optional[str], child_id: str, text: str
    ) -> Dict[str, Any]:
        # 1. 验证 child_id
        child_stmt = select(ChildProfile).where(ChildProfile.id == child_id)
        child = (await self.db.execute(child_stmt)).scalar_one_or_none()
        if not child:
            raise ValueError("孩子档案不存在")

        # 2. 获取或创建会话
        if conversation_id:
            conv_stmt = select(Conversation).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.child_id == child_id,
                )
            )
            conversation = (await self.db.execute(conv_stmt)).scalar_one_or_none()
        else:
            conversation = None

        if not conversation:
            conversation = Conversation(
                id=str(uuid.uuid4()),
                child_id=child_id,
                owner_user_id=user_id,
                title="家庭对话",
            )
            self.db.add(conversation)
            await self.db.flush()

        # 3. 加密存储原始消息
        msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            child_id=child_id,
            sender_user_id=user_id,
            sender_role="child",
            message_type="text",
            direction="child_to_ai",
            content_enc=aes_encrypt(text, settings.ENCRYPTION_AES_KEY),
            level=0,
            status="active",
            source_message_hash=text_hash(text),
        )
        self.db.add(msg)
        await self.db.flush()

        # 4. 安全检测
        safety_event_id: Optional[str] = None
        if needs_safety_check(text):
            patterns = detect_patterns(text)
            event = SafetyEvent(
                id=str(uuid.uuid4()),
                child_id=child_id,
                source_message_id=msg.id,
                source_type="child_message",
                patterns=json.dumps(patterns),
                status="pending",
            )
            self.db.add(event)
            await self.db.flush()
            safety_event_id = event.id

        # 5. 记忆提取（最近 7 天摘要）
        memory_prompt = await self._build_memory_context(child_id)

        # 6. LLM 生成草稿（降敏摘要）
        draft_dict: Optional[Dict[str, Any]] = None
        source = "fallback"

        if not safety_event_id:  # 高风险不自动生成草稿
            if llm_client.is_configured():
                user_prompt = f"用户消息（脱敏摘要，不包含具体细节）：{text[:500]}\n请生成降敏摘要，不要包含任何具体细节。"
                draft_dict = await llm_client.generate_json(
                    DRAFT_SYSTEM_PROMPT, user_prompt
                )

            if not draft_dict:
                draft_dict = generate_draft_fallback(text)
                source = "fallback"
            else:
                source = "llm"

        # 7. 创建草稿（等待用户确认）
        draft_id: Optional[str] = None
        draft_obj: Optional[Dict[str, Any]] = None

        if draft_dict:
            body_text = draft_dict.get("body", "")
            body_enc = aes_encrypt(body_text, settings.ENCRYPTION_AES_KEY)

            draft = Draft(
                id=str(uuid.uuid4()),
                child_id=child_id,
                source_message_id=msg.id,
                conversation_id=conversation.id,
                title_enc=aes_encrypt(
                    draft_dict.get("title", "孩子想跟你聊聊"),
                    settings.ENCRYPTION_AES_KEY,
                ),
                body_enc=body_enc,
                suggestions_json=json.dumps(draft_dict.get("suggestions", [])),
                status="preview",
            )
            self.db.add(draft)
            await self.db.flush()
            draft_id = draft.id
            draft_obj = {
                "draft_id": draft.id,
                "title": draft_dict.get("title"),
                "body": body_text,
                "level": 3,
                "scope": "guardians",
                "source": source,
            }

        # 8. 静默写入工作记忆（仅 AI 用，L0 级别）
        await self._append_working_memory(
            child_id=child_id,
            source_message_id=msg.id,
            raw_text=text,
            explainable_summary=None,
            level=0,
        )

        # 9. 审计日志
        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=child_id,
            actor_user_id=user_id,
            action="child_message_sent",
            entity_type="message",
            entity_id=msg.id,
            level=0,
            ip_address=None,
            user_agent=None,
            changes_json=json.dumps({"message_type": "text", "has_safety_check": safety_event_id is not None}),
        )
        self.db.add(audit)
        await self.db.commit()

        return {
            "message_id": msg.id,
            "conversation_id": conversation.id,
            "needs_safety_check": safety_event_id is not None,
            "safety_event_id": safety_event_id,
            "draft": draft_obj,
            "source": source,
        }

    # ========== 草稿确认 → 分享 ==========
    async def confirm_and_share(
        self,
        user_id: str,
        draft_id: str,
        to_role: str,
        level: int,
    ) -> Dict[str, Any]:
        draft_stmt = select(Draft).where(Draft.id == draft_id)
        draft = (await self.db.execute(draft_stmt)).scalar_one_or_none()
        if not draft:
            raise ValueError("草稿不存在")
        if draft.status != "preview":
            raise ValueError("草稿状态异常")

        title = aes_decrypt(draft.title_enc, settings.ENCRYPTION_AES_KEY)
        body = aes_decrypt(draft.body_enc, settings.ENCRYPTION_AES_KEY)

        # 分享权限
        share = SharePermission(
            id=str(uuid.uuid4()),
            child_id=draft.child_id,
            source_message_id=draft.source_message_id,
            source_draft_id=draft.id,
            granted_by_user_id=user_id,
            share_to_role=to_role,
            level=level,
            status="active",
        )
        self.db.add(share)
        await self.db.flush()

        # 收件箱消息
        inbox = InboxMessage(
            id=str(uuid.uuid4()),
            child_id=draft.child_id,
            share_id=share.id,
            from_role="child",
            to_role=to_role,
            title_enc=draft.title_enc,
            body_enc=draft.body_enc,
            level=level,
            status="delivered",
            permission_id=share.id,
        )
        self.db.add(inbox)
        await self.db.flush()

        # 更新草稿状态
        draft.status = "confirmed"
        draft.to_role = to_role
        draft.level = level

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=draft.child_id,
            actor_user_id=user_id,
            action="share_confirmed",
            entity_type="share_permission",
            entity_id=share.id,
            level=level,
            changes_json=json.dumps({"to_role": to_role, "level": level}),
        )
        self.db.add(audit)
        await self.db.commit()

        return {
            "share_id": share.id,
            "inbox_message_id": inbox.id,
            "delivered_to": to_role,
            "title": title,
            "body": body,
        }

    # ========== 撤回分享 ==========
    async def revoke_share(
        self, user_id: str, share_id: str
    ) -> Dict[str, Any]:
        share_stmt = select(SharePermission).where(
            and_(SharePermission.id == share_id, SharePermission.status == "active")
        )
        share = (await self.db.execute(share_stmt)).scalar_one_or_none()
        if not share:
            raise ValueError("分享不存在或已撤回")

        share.status = "revoked"

        # 影响的收件箱
        inbox_stmt = select(InboxMessage).where(
            InboxMessage.share_id == share_id
        )
        inboxes = (await self.db.execute(inbox_stmt)).scalars().all()
        affected_ids = []
        for inbox in inboxes:
            inbox.status = "revoked"
            affected_ids.append(inbox.id)

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=share.child_id,
            actor_user_id=user_id,
            action="share_revoked",
            entity_type="share_permission",
            entity_id=share.id,
            level=share.level,
        )
        self.db.add(audit)
        await self.db.commit()

        return {"revoked": True, "affected_inbox_ids": affected_ids}

    # ========== 回复（家长/老师 → 孩子）==========
    async def reply_to_child(
        self,
        user_id: str,
        user_role: str,
        child_id: str,
        to_role: str,
        body: str,
        source_inbox_id: Optional[str],
    ) -> Dict[str, Any]:
        body_enc = aes_encrypt(body, settings.ENCRYPTION_AES_KEY)

        msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=None,
            child_id=child_id,
            sender_user_id=user_id,
            sender_role=user_role,
            message_type="text",
            direction="support_to_child",
            content_enc=body_enc,
            level=2,
            status="active",
            source_message_hash=text_hash(body),
        )
        self.db.add(msg)
        await self.db.flush()

        title = f"{self._role_display(user_role)} 想跟你聊聊"
        inbox = InboxMessage(
            id=str(uuid.uuid4()),
            child_id=child_id,
            share_id=None,
            from_role=user_role,
            to_role=to_role,
            title_enc=aes_encrypt(title, settings.ENCRYPTION_AES_KEY),
            body_enc=body_enc,
            level=2,
            status="delivered",
            permission_id=None,
        )
        self.db.add(inbox)

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=child_id,
            actor_user_id=user_id,
            action="support_reply",
            entity_type="inbox_message",
            entity_id=inbox.id,
            level=2,
            changes_json=json.dumps({"to_role": to_role, "source_inbox_id": source_inbox_id}),
        )
        self.db.add(audit)
        await self.db.commit()

        return {"reply_id": msg.id, "inbox_message_id": inbox.id}

    # ========== 收件箱列表 ==========
    async def inbox_list(
        self, user_id: str, user_role: str, child_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        stmt = select(InboxMessage).where(InboxMessage.to_role == user_role)
        if child_id:
            stmt = stmt.where(InboxMessage.child_id == child_id)
        stmt = stmt.order_by(InboxMessage.created_at.desc())
        items = (await self.db.execute(stmt)).scalars().all()

        results = []
        for item in items:
            title = aes_decrypt(item.title_enc, settings.ENCRYPTION_AES_KEY)
            body = aes_decrypt(item.body_enc, settings.ENCRYPTION_AES_KEY)
            results.append(
                {
                    "id": item.id,
                    "child_id": item.child_id,
                    "from_role": item.from_role,
                    "title": title,
                    "body": body,
                    "level": item.level,
                    "read": item.read,
                    "delivered_at": item.created_at,
                    "status": item.status,
                }
            )
        return results

    # ========== 内部辅助 ==========
    async def _build_memory_context(self, child_id: str) -> str:
        """构建 LLM 用的记忆上下文（仅摘要，不含原文）"""
        since = datetime.utcnow() - timedelta(days=7)
        stmt = (
            select(MemoryItem)
            .where(
                and_(
                    MemoryItem.child_id == child_id,
                    MemoryItem.status == "active",
                    MemoryItem.created_at >= since,
                )
            )
            .order_by(MemoryItem.created_at.desc())
            .limit(10)
        )
        items = (await self.db.execute(stmt)).scalars().all()
        if not items:
            return ""

        parts = []
        for item in items:
            summary = item.explainable_summary_enc
            if summary:
                try:
                    decoded = aes_decrypt(summary, settings.ENCRYPTION_AES_KEY)
                    parts.append(f"- [{item.type}] {decoded}")
                except Exception:
                    continue
        return "\n".join(parts)

    async def _append_working_memory(
        self,
        child_id: str,
        source_message_id: str,
        raw_text: str,
        explainable_summary: Optional[str],
        level: int,
    ) -> None:
        summary = explainable_summary or "近期有想聊的事，暂存。"
        memory = MemoryItem(
            id=str(uuid.uuid4()),
            child_id=child_id,
            source_message_id=source_message_id,
            type="working_memory",
            raw_content_enc=aes_encrypt(raw_text, settings.ENCRYPTION_AES_KEY),
            explainable_summary_enc=aes_encrypt(summary, settings.ENCRYPTION_AES_KEY),
            level=level,
            status="active",
            approved_by_child=False,
        )
        self.db.add(memory)

    @staticmethod
    def _role_display(role: str) -> str:
        return {
            "child": "孩子",
            "parent": "家长",
            "teacher": "老师",
            "counselor": "心理老师",
        }.get(role, role)
