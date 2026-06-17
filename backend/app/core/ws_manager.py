import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket


@dataclass
class Connection:
    connection_id: str
    user_id: Optional[str] = None
    child_id: Optional[str] = None
    role: Optional[str] = None
    ws: Optional[WebSocket] = None


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: Dict[str, Connection] = {}
        self._user_connections: Dict[str, Set[str]] = {}
        self._child_connections: Dict[str, Set[str]] = {}

    def gen_connection_id(self) -> str:
        return str(uuid.uuid4())

    def connect(
        self,
        ws: WebSocket,
        user_id: Optional[str] = None,
        child_id: Optional[str] = None,
        role: Optional[str] = None,
        connection_id: Optional[str] = None,
    ) -> Connection:
        cid = connection_id or self.gen_connection_id()
        conn = Connection(
            connection_id=cid,
            user_id=user_id,
            child_id=child_id,
            role=role,
            ws=ws,
        )
        self._connections[cid] = conn
        if user_id is not None:
            self._user_connections.setdefault(user_id, set()).add(cid)
        if child_id is not None:
            self._child_connections.setdefault(child_id, set()).add(cid)
        return conn

    def disconnect(self, connection_id: str) -> None:
        conn = self._connections.pop(connection_id, None)
        if conn is None:
            return
        if conn.user_id is not None and conn.user_id in self._user_connections:
            self._user_connections[conn.user_id].discard(connection_id)
            if not self._user_connections[conn.user_id]:
                del self._user_connections[conn.user_id]
        if conn.child_id is not None and conn.child_id in self._child_connections:
            self._child_connections[conn.child_id].discard(connection_id)
            if not self._child_connections[conn.child_id]:
                del self._child_connections[conn.child_id]

    async def _send_text(self, ws: WebSocket, message: str) -> None:
        try:
            await ws.send_text(message)
        except Exception:
            pass

    async def _send_json(self, ws: WebSocket, data: Any) -> None:
        try:
            text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
            await self._send_text(ws, text)
        except Exception:
            pass

    async def send_to_user(self, user_id: str, message: Any) -> None:
        for cid in self._user_connections.get(user_id, set()).copy():
            conn = self._connections.get(cid)
            if conn is None or conn.ws is None:
                continue
            await self._send_json(conn.ws, message)

    async def send_to_connection(self, connection_id: str, message: Any) -> None:
        conn = self._connections.get(connection_id)
        if conn is None or conn.ws is None:
            return
        await self._send_json(conn.ws, message)

    async def broadcast_to_child_role(self, child_id: str, role: str, message: Any) -> None:
        for cid in self._child_connections.get(child_id, set()).copy():
            conn = self._connections.get(cid)
            if conn is None or conn.ws is None:
                continue
            if conn.role != role:
                continue
            await self._send_json(conn.ws, message)

    async def broadcast_to_child_except_role(self, child_id: str, role: str, message: Any) -> None:
        for cid in self._child_connections.get(child_id, set()).copy():
            conn = self._connections.get(cid)
            if conn is None or conn.ws is None:
                continue
            if conn.role == role:
                continue
            await self._send_json(conn.ws, message)

    async def broadcast_to_child(self, child_id: str, message: Any) -> None:
        for cid in self._child_connections.get(child_id, set()).copy():
            conn = self._connections.get(cid)
            if conn is None or conn.ws is None:
                continue
            await self._send_json(conn.ws, message)

    def user_connection_count(self, user_id: str) -> int:
        return len(self._user_connections.get(user_id, set()))

    def child_connection_count(self, child_id: str) -> int:
        return len(self._child_connections.get(child_id, set()))

    def total_connections(self) -> int:
        return len(self._connections)


manager = ConnectionManager()
