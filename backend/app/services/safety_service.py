"""
安全事件处理 - 孩子确认高风险消息的处理分支
"""

import uuid
import json
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.safety_events import SafetyEvent
from app.db.models.audit_logs import AuditLog
from app.core.llm_client import llm_client
from app.core.llm_prompts import PARENT_GUIDE_SYSTEM_PROMPT
from app.core.llm_fallback import (
    generate_parent_guide_fallback,
    SAFETY_RESOURCES,
)


class SafetyService:
    VALID_BRANCHES = ["safe_continue", "unsafe_support", "escalation"]

    def __init__(self, db: AsyncSession):
        self.db = db

    def check_text(self, text: str) -> Dict[str, Any]:
        from app.core.safety_patterns import needs_safety_check, detect_patterns

        return {
            "needs_check": needs_safety_check(text),
            "patterns": detect_patterns(text),
        }

    async def resolve_event(
        self,
        user_id: str,
        safety_event_id: str,
        branch: str,
    ) -> Dict[str, Any]:
        if branch not in self.VALID_BRANCHES:
            raise ValueError(f"无效分支: {branch}")

        stmt = select(SafetyEvent).where(
            and_(SafetyEvent.id == safety_event_id, SafetyEvent.status == "pending")
        )
        event = (await self.db.execute(stmt)).scalar_one_or_none()
        if not event:
            raise ValueError("安全事件不存在或已处理")

        # 权限校验：只有该孩子本人能解决自己的安全事件
        from app.services.permission_service import PermissionService

        perm = PermissionService(self.db)
        if not await perm.child_owns_profile(user_id, event.child_id):
            raise PermissionError("无权处理该安全事件")

        event.status = branch
        event.resolved_by_user_id = user_id
        event.resolved_at = datetime.utcnow()

        resources_shown = False
        llm_called = False
        message = "已记录你的选择。"

        if branch == "escalation":
            # 立即显示本地资源，不调用 LLM（避免延误）
            event.safety_resources_json = json.dumps(
                SAFETY_RESOURCES["escalation"]
            )
            resources_shown = True
            message = SAFETY_RESOURCES["escalation"]["message"]

        elif branch == "unsafe_support":
            event.safety_resources_json = json.dumps(
                SAFETY_RESOURCES["unsafe_support"]
            )
            resources_shown = True
            message = SAFETY_RESOURCES["unsafe_support"]["message"]

        elif branch == "safe_continue":
            # 仅记录，不立即调用 LLM
            message = "好的。下次你想聊的时候，随时告诉我。不急。"

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=event.child_id,
            actor_user_id=user_id,
            action=f"safety_resolve_{branch}",
            entity_type="safety_event",
            entity_id=safety_event_id,
            level=2,
            changes_json=json.dumps({"branch": branch}),
        )
        self.db.add(audit)
        await self.db.commit()

        return {
            "resolved_at": event.resolved_at,
            "resources_shown": resources_shown,
            "llm_called": llm_called,
            "message": message,
        }
