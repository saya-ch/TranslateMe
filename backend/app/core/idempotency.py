import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


STATUS_IN_FLIGHT = "in_flight"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"


@dataclass
class IdempotencyRequest:
    user_id: str
    client_request_id: str
    endpoint: str
    request_hash: str
    response_json: Optional[str]
    status: str
    created_at: datetime
    expires_at: datetime


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _compute_request_hash(endpoint: str, request_body: Any) -> str:
    if isinstance(request_body, str):
        serialized = request_body
    else:
        try:
            serialized = json.dumps(request_body, sort_keys=True, ensure_ascii=False)
        except Exception:
            serialized = str(request_body)
    raw = f"{endpoint}|{serialized}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


async def _fetch_record(
    db: AsyncSession,
    user_id: str,
    client_request_id: str,
) -> Optional[dict]:
    result = await db.execute(
        text(
            """
            SELECT user_id, client_request_id, endpoint, request_hash,
                   response_json, status, created_at, expires_at
            FROM idempotency_requests
            WHERE user_id = :user_id AND client_request_id = :client_request_id
            """
        ),
        {"user_id": user_id, "client_request_id": client_request_id},
    )
    row = result.mappings().first()
    if row is None:
        return None
    return dict(row)


async def _insert_in_flight(
    db: AsyncSession,
    user_id: str,
    client_request_id: str,
    endpoint: str,
    request_hash: str,
    expires_at: datetime,
) -> bool:
    try:
        await db.execute(
            text(
                """
                INSERT INTO idempotency_requests
                    (user_id, client_request_id, endpoint, request_hash,
                     response_json, status, created_at, expires_at)
                VALUES (:user_id, :client_request_id, :endpoint, :request_hash,
                        NULL, :status, :created_at, :expires_at)
                """
            ),
            {
                "user_id": user_id,
                "client_request_id": client_request_id,
                "endpoint": endpoint,
                "request_hash": request_hash,
                "status": STATUS_IN_FLIGHT,
                "created_at": _utcnow(),
                "expires_at": expires_at,
            },
        )
        await db.commit()
        return True
    except Exception:
        await db.rollback()
        return False


async def _update_record(
    db: AsyncSession,
    user_id: str,
    client_request_id: str,
    status: str,
    response_json: Optional[str],
    expires_at: datetime,
) -> None:
    await db.execute(
        text(
            """
            UPDATE idempotency_requests
            SET status = :status,
                response_json = :response_json,
                expires_at = :expires_at
            WHERE user_id = :user_id AND client_request_id = :client_request_id
            """
        ),
        {
            "status": status,
            "response_json": response_json,
            "expires_at": expires_at,
            "user_id": user_id,
            "client_request_id": client_request_id,
        },
    )
    await db.commit()


class IdempotencyConflict(Exception):
    pass


async def with_idempotency(
    db: AsyncSession,
    user_id: str,
    client_request_id: str,
    endpoint: str,
    request_body: Any,
    handler: Callable[..., Awaitable[dict]],
    ttl_hours: int = 24,
) -> dict:
    if not user_id or not client_request_id:
        return await handler()

    request_hash = _compute_request_hash(endpoint, request_body)
    expires_at = _utcnow() + timedelta(hours=ttl_hours)

    existing = await _fetch_record(db, user_id, client_request_id)

    if existing is not None:
        status = existing.get("status")
        if status == STATUS_COMPLETED and existing.get("response_json"):
            try:
                return json.loads(existing["response_json"])
            except json.JSONDecodeError:
                logger.warning("Cached response JSON invalid for %s", client_request_id)
        elif status == STATUS_IN_FLIGHT:
            raise IdempotencyConflict("Request already in flight")
        elif status == STATUS_FAILED:
            pass

    inserted = await _insert_in_flight(
        db, user_id, client_request_id, endpoint, request_hash, expires_at
    )
    if not inserted:
        existing = await _fetch_record(db, user_id, client_request_id)
        if existing is not None and existing.get("status") == STATUS_IN_FLIGHT:
            raise IdempotencyConflict("Request already in flight")
        if existing is not None and existing.get("status") == STATUS_COMPLETED and existing.get("response_json"):
            try:
                return json.loads(existing["response_json"])
            except json.JSONDecodeError:
                pass

    try:
        response = await handler()
    except Exception:
        await _update_record(
            db, user_id, client_request_id, STATUS_FAILED, None, expires_at
        )
        raise

    try:
        response_json = json.dumps(response, ensure_ascii=False)
    except TypeError:
        response_json = json.dumps({"result": str(response)}, ensure_ascii=False)

    await _update_record(
        db, user_id, client_request_id, STATUS_COMPLETED, response_json, expires_at
    )

    return response


async def cleanup_expired(db: AsyncSession) -> int:
    result = await db.execute(
        text(
            """
            DELETE FROM idempotency_requests
            WHERE expires_at < :now
            """
        ),
        {"now": _utcnow()},
    )
    await db.commit()
    return int(result.rowcount or 0)
