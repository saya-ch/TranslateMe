# 以孩子为中心的家庭组 AI 沟通中枢

一个围绕青少年孩子构建的私密沟通系统。核心设计原则是：**孩子的信息默认仅孩子本人和 AI 可读取**，对外分享需要孩子明确确认。

## 架构

```
孩子消息 → 安全检测 (高风险) → 降敏草稿 → 孩子确认 → 分享给家长/老师
                                      ↓
                                工作记忆 (L0 级别，仅 AI 用)

家长/老师提问 → 权限防火墙 (追问具体内容会被拒绝) → 通用沟通建议
```

## 核心功能

- **三级记忆系统**：原始会话 / 工作记忆 (L0) / 家庭共享记忆 (L2+)
- **信息权限分级**：L0 完全私密 → L1 仅提醒 → L2 类别分享 → L3 降敏摘要 → L4 原话分享
- **安全检测**：检测自杀/自残/伤害他人等高风险表达，提供本地紧急资源
- **权限防火墙**：家长/老师追问孩子未授权的具体内容会被自动拒绝
- **审计日志**：所有敏感操作都有记录
- **实时通知**：WebSocket 支持多连接 per 用户

## 技术栈

- **后端**：FastAPI + Pydantic v2 + Uvicorn
- **数据库**：MySQL 8.0 + SQLAlchemy 2.x + Alembic
- **认证**：JWT (python-jose)
- **加密**：AES-256-GCM (敏感内容存储)
- **AI**：OpenAI 兼容 API，失败回退到本地模板

## 快速开始

```bash
# 1. 启动 MySQL
cd backend
docker compose up -d

# 2. 安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 创建种子数据（演示账号）
python seed.py

# 4. 启动服务
python -m app.main
# 或: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文档: http://localhost:8000/docs

## 演示账号

| 用户名 | 密码 | 角色 |
|-------|------|------|
| kid_demo | child123 | 孩子 |
| parent_demo | parent123 | 家长 |
| teacher_demo | teacher123 | 老师 |

## 主要 API 端点

| 方法 | 路径 | 描述 |
|-----|------|------|
| POST | `/api/v1/auth/register` | 注册 |
| POST | `/api/v1/auth/login` | 登录 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |
| POST | `/api/v1/conversations/chat` | 孩子发送消息 |
| POST | `/api/v1/conversations/drafts/{id}/confirm` | 孩子确认并分享 |
| POST | `/api/v1/conversations/shares/{id}/revoke` | 孩子撤回分享 |
| POST | `/api/v1/conversations/reply` | 家长/老师回复孩子 |
| GET | `/api/v1/conversations/inbox` | 我的收件箱 |
| GET | `/api/v1/memory/{child_id}` | 孩子查看自己的记忆 |
| DELETE | `/api/v1/memory/{child_id}/{memory_id}` | 孩子删除记忆 |
| POST | `/api/v1/safety/events/{id}/resolve` | 处理高风险消息 |
| POST | `/api/v1/llm/parent-ask` | 家长向 AI 提问（带防火墙） |
| POST | `/api/v1/llm/teacher-ask` | 老师向 AI 提问 |
| WS | `/api/v1/ws?token=...&child_id=...` | 实时通知 WebSocket |

## 数据库表

| 表名 | 描述 |
|-----|------|
| users | 用户 |
| child_profiles | 孩子档案 |
| family_groups | 家庭组 |
| group_members | 组成员 |
| conversations | 会话 |
| messages | 消息 |
| drafts | 草稿 |
| share_permissions | 分享授权 |
| inbox_messages | 收件箱消息 |
| memory_items | 记忆条目 |
| safety_events | 安全事件 |
| consents | 授权记录 |
| audit_logs | 审计日志 |
| idempotency_keys | 幂等键 |

## 安全设计要点

1. **敏感内容加密存储**：所有消息正文使用 AES-256-GCM 加密
2. **默认最小权限**：孩子的消息默认 L0 级别，仅本人和 AI 可读取
3. **孩子确认优先**：对外分享必须经过孩子明确确认
4. **权限防火墙**：检测家长/老师的追问模式，自动拒绝泄露具体内容
5. **高风险本地处理**：提到伤害自己/他人时，优先展示本地紧急资源，不调用 LLM
6. **完整审计**：所有敏感操作都有不可修改的审计记录

## 数据库迁移（Alembic）

```bash
cd backend
alembic init migrations
# 编辑 alembic.ini 和 migrations/env.py 配置数据库
alembic revision --autogenerate -m "initial"
alembic upgrade head
```
