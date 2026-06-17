"""
记忆服务 - 孩子可以查看、确认、删除自己的记忆条目
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.models.memory_items import MemoryItem
from app.db.models.share_permissions import SharePermission
from app.db.models.audit_logs import AuditLog
from app.core.security import aes_decrypt, aes_encrypt
from app.config import settings


class MemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_memory(self, child_id: str) -> List[Dict[str, Any]]:
        stmt = (
            select(MemoryItem)
            .where(
                and_(
                    MemoryItem.child_id == child_id,
                    MemoryItem.status == "active",
                )
            )
            .order_by(MemoryItem.created_at.desc())
            .limit(50)
        )
        items = (await self.db.execute(stmt)).scalars().all()
        results = []
        for item in items:
            summary = None
            if item.explainable_summary_enc:
                try:
                    summary = aes_decrypt(
                        item.explainable_summary_enc, settings.ENCRYPTION_AES_KEY
                    )
                except Exception:
                    summary = None
            results.append(
                {
                    "id": item.id,
                    "type": item.type,
                    "explainable_summary": summary,
                    "level": item.level,
                    "status": item.status,
                }
            )
        return results

    async def delete_memory(
        self, child_id: str, memory_id: str, actor_user_id: str
    ) -> Dict[str, Any]:
        stmt = select(MemoryItem).where(
            and_(MemoryItem.id == memory_id, MemoryItem.child_id == child_id)
        )
        memory = (await self.db.execute(stmt)).scalar_one_or_none()
        if not memory:
            raise ValueError("记忆条目不存在")

        memory.status = "deleted"

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=child_id,
            actor_user_id=actor_user_id,
            action="memory_deleted",
            entity_type="memory_item",
            entity_id=memory_id,
            level=memory.level,
        )
        self.db.add(audit)
        await self.db.commit()

        return {"deleted": True, "memory_id": memory_id}

    async def approve_memory_level(
        self, child_id: str, memory_id: str, level: int, actor_user_id: str
    ) -> Dict[str, Any]:
        stmt = select(MemoryItem).where(
            and_(MemoryItem.id == memory_id, MemoryItem.child_id == child_id)
        )
        memory = (await self.db.execute(stmt)).scalar_one_or_none()
        if not memory:
            raise ValueError("记忆条目不存在")

        memory.level = level
        memory.approved_by_child = True

        audit = AuditLog(
            id=str(uuid.uuid4()),
            child_id=child_id,
            actor_user_id=actor_user_id,
            action="memory_level_approved",
            entity_type="memory_item",
            entity_id=memory_id,
            level=level,
            changes_json=json.dumps({"new_level": level}),
        )
        self.db.add(audit)
        await self.db.commit()

        return {"memory_id": memory_id, "level": level, "approved": True}
