"""
WebSocket 连接管理 - 支持多连接 per 用户，按 child/role 路由
"""

import uuid
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket


class Connection:
    __slots__ = ("id", "user_id", "child_id", "role", "ws")

    def __init__(self, id: str, user_id: str, child_id: str, role: str, ws: WebSocket):
        self.id = id
        self.user_id = user_id
        self.child_id = child_id
        self.role = role
        self.ws = ws


class WebSocketManager:
    def __init__(self):
        self._connections: Dict[str, Connection] = {}
        self._by_user: Dict[str, Set[str]] = {}
        self._by_child: Dict[str, Dict[str, Set[str]]] = {}  # child_id -> {role -> {conn_ids}}

    async def connect(self, ws: WebSocket, user_id: str, child_id: str, role: str) -> str:
        await ws.accept()
        conn_id = str(uuid.uuid4())
        conn = Connection(conn_id, user_id, child_id, role, ws)
        self._connections[conn_id] = conn

        if user_id not in self._by_user:
            self._by_user[user_id] = set()
        self._by_user[user_id].add(conn_id)

        if child_id not in self._by_child:
            self._by_child[child_id] = {}
        if role not in self._by_child[child_id]:
            self._by_child[child_id][role] = set()
        self._by_child[child_id][role].add(conn_id)

        return conn_id

    def disconnect(self, conn_id: str) -> None:
        conn = self._connections.pop(conn_id, None)
        if not conn:
            return

        user_set = self._by_user.get(conn.user_id)
        if user_set:
            user_set.discard(conn_id)
            if not user_set:
                del self._by_user[conn.user_id]

        role_map = self._by_child.get(conn.child_id)
        if role_map:
            role_set = role_map.get(conn.role)
            if role_set:
                role_set.discard(conn_id)
                if not role_set:
                    del role_map[conn.role]
            if not role_map:
                del self._by_child[conn.child_id]

    async def send_to_user(self, user_id: str, message: dict) -> int:
        conn_ids = list(self._by_user.get(user_id, set()))
        sent = 0
        for conn_id in conn_ids:
            conn = self._connections.get(conn_id)
            if conn:
                try:
                    await conn.ws.send_json(message)
                    sent += 1
                except Exception:
                    pass
        return sent

    async def send_to_child_role(self, child_id: str, role: str, message: dict) -> int:
        role_map = self._by_child.get(child_id, {})
        conn_ids = list(role_map.get(role, set()))
        sent = 0
        for conn_id in conn_ids:
            conn = self._connections.get(conn_id)
            if conn:
                try:
                    await conn.ws.send_json(message)
                    sent += 1
                except Exception:
                    pass
        return sent

    async def broadcast_to_child(self, child_id: str, message: dict, allowed_roles=None) -> int:
        role_map = self._by_child.get(child_id, {})
        sent = 0
        for role, conn_ids in role_map.items():
            if allowed_roles and role not in allowed_roles:
                continue
            for conn_id in list(conn_ids):
                conn = self._connections.get(conn_id)
                if conn:
                    try:
                        await conn.ws.send_json(message)
                        sent += 1
                    except Exception:
                        pass
        return sent

    def count_connections(self, user_id: Optional[str] = None) -> int:
        if user_id:
            return len(self._by_user.get(user_id, set()))
        return len(self._connections)


ws_manager = WebSocketManager()
