"""
家长/老师向 AI 提问的服务 - 带权限防火墙
不透露孩子未授权分享的具体内容
"""

import uuid
import json
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.child_profiles import ChildProfile
from app.db.models.share_permissions import SharePermission
from app.db.models.audit_logs import AuditLog
from app.core.llm_client import llm_client
from app.core.llm_prompts import PARENT_GUIDE_SYSTEM_PROMPT, TEACHER_GUIDE_SYSTEM_PROMPT
from app.core.llm_fallback import (
    generate_parent_guide_fallback,
    generate_teacher_guide_fallback,
    is_firewall_probing,
)


class LLMOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def parent_ask(self, user_id: str, child_id: str, question: str) -> Dict[str, Any]:
        # 权限防火墙：检测是否在追问未授权的具体内容
        is_probing = is_firewall_probing(question)
        if is_probing:
            # 直接返回通用建议，不调用 LLM
            fallback = generate_parent_guide_fallback(question)
            fallback["_note"] = "检测到你在追问孩子的具体内容；未经孩子同意，我不能透露具体内容。"
            return {
                "source": "firewall",
                "is_probing": True,
                "content": fallback,
            }

        # 检查 LLM 是否可用
        content = None
        source = "fallback"

        if llm_client.is_configured():
            user_prompt = f"家长问题（通用场景，不针对具体孩子）：{question[:500]}"
            content = await llm_client.generate_json(
                PARENT_GUIDE_SYSTEM_PROMPT, user_prompt
            )
            if content:
                source = "llm"

        if not content:
            content = generate_parent_guide_fallback(question)
            source = "fallback"

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=child_id,
            actor_user_id=user_id,
            action="parent_llm_ask",
            entity_type="llm_response",
            entity_id="",
            level=1,
            changes_json=json.dumps({"source": source, "is_probing": False}),
        )
        self.db.add(audit)
        await self.db.commit()

        return {"source": source, "is_probing": False, "content": content}

    async def teacher_ask(self, user_id: str, child_id: str, observation: str) -> Dict[str, Any]:
        content = None
        source = "fallback"

        if llm_client.is_configured():
            user_prompt = f"老师观察（通用场景）：{observation[:500]}"
            content = await llm_client.generate_json(
                TEACHER_GUIDE_SYSTEM_PROMPT, user_prompt
            )
            if content:
                source = "llm"

        if not content:
            content = generate_teacher_guide_fallback(observation)
            source = "fallback"

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=child_id,
            actor_user_id=user_id,
            action="teacher_llm_ask",
            entity_type="llm_response",
            entity_id="",
            level=1,
        )
        self.db.add(audit)
        await self.db.commit()

        return {"source": source, "content": content}
