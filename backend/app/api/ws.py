"""
WebSocket 路由 - 实时通知
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.core.ws_manager import ws_manager
from app.core.security import decode_jwt

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    child_id: str = Query(...),
):
    # 认证
    payload = decode_jwt(token)
    if not payload:
        await websocket.close(code=4001, reason="无效 token")
        return

    user_id = payload.get("user_id")
    role = payload.get("role")
    if not user_id or not role:
        await websocket.close(code=4002, reason="token 缺少必要字段")
        return

    # 连接管理
    conn_id = await ws_manager.connect(websocket, user_id, child_id, role)

    try:
        # 发送欢迎消息
        await websocket.send_json(
            {"type": "connected", "connection_id": conn_id, "role": role}
        )

        # 保持连接，接收心跳
        while True:
            try:
                data = await websocket.receive_text()
                # 简单的 ping/pong
                try:
                    msg = json.loads(data)
                    if msg.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except Exception:
                    pass
            except WebSocketDisconnect:
                break
    finally:
        ws_manager.disconnect(conn_id)
