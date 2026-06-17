# 帮我说出口 · TranslateMe

> 一个围绕孩子建立的私密沟通中枢。AI 可以分别听见孩子、家长、老师的真实想法，但不会自动泄露任何一方原话。

TRAE AI 创造力大赛初赛作品 · 社会服务赛道 · 社会公益 / 青少年身心健康方向。

## 项目简介

很多初高中学生遇到学习压力、同伴关系、亲子冲突时，不是不想求助，而是不知道怎么开口，也怕一开口就被评价。他们真实说出口的话可能只有："我很烦""我不想去学校""你们不懂我"。

**帮我说出口** 不是 AI 心理咨询师，也不是情绪陪聊机器人。它是一个以孩子为中心的沟通桥梁：AI 作为受托的中间人，分别听见三方想法，但只在用户明确授权后，把可分享的信息转成温和、低冲突、可理解的沟通内容。

## 核心闭环

### 孩子端
1. 私密倾诉（默认只有自己能看到）
2. 安全确认（命中高风险表达时，两路分支）
3. AI 帮孩子整理：我真正想表达什么 / 我怕什么 / 我希望大人怎么做
4. 选择分享范围：只让自己看 / 生成草稿自己发 / 发给家长 / 只发模糊提醒
5. 预览草稿（可编辑）→ 确认发送
6. 收件箱接收家长回应

### 家长端
1. 收件箱看到孩子的沟通请求（温和摘要，非原话）
2. 问 AI 怎么回应
3. AI 给通用沟通建议（含信息防火墙说明，不透露孩子未授权内容）
4. 回应草稿（可编辑）→ 确认发送给孩子

### 老师端
1. 记录观察（不直接变成对家长的告知）
2. AI 给谈话建议、观察点、转介建议
3. 选择只记录或之后走学校心理老师/家校沟通流程

## 信息防火墙

- 原话默认不共享
- 具体事实默认不共享
- 只共享用户明确允许的内容
- 未授权时只给对方通用沟通建议
- 分享前必须让用户确认
- 对方不能通过追问套出孩子隐私
- AI 不能说"孩子其实告诉我……"

详见 [docs/safety-boundary.md](docs/safety-boundary.md)。

## 安全确认

"高风险表达"不等于系统判定孩子有危险。命中后进入安全确认页，由用户自己选择：

- **我现在安全，只是想整理表达**：可继续整理流程
- **我不太安全 / 我身边马上有危险**：只显示支持资源（12355/12356 心理支持；110/120 立即人身危险）

不询问危险方式、地点、计划，不输出任何危险行为方法。

## 技术栈

- **前端**：Vite + React + TypeScript，移动优先
- **后端**：FastAPI + Pydantic v2 + Uvicorn
- **数据库**：MySQL 8.0 + SQLAlchemy 2.x (async)
- **认证**：JWT (python-jose)
- **加密**：AES-256-GCM（敏感内容存储）
- **AI**：OpenAI 兼容 API，失败回退本地模板
- **权限**：统一 PermissionService 校验孩子/家庭组访问关系

前端默认走后端 API；后端不可达时自动回退本地 messageStore 模拟，保证 Demo 可用。

## 安装与运行

### 前端

```bash
# 安装依赖
npm install

# 本地开发（默认 http://localhost:5173）
npm run dev

# 类型检查
npm run lint

# 构建
npm run build

# 预览构建产物
npm run preview
```

前端通过 `VITE_API_BASE` 指定后端地址，默认 `http://localhost:8000/api/v1`。

### 后端

```bash
cd backend

# 1. 启动 MySQL（或使用已有实例）
docker compose up -d

# 2. 安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env  # 按需修改数据库连接、JWT 密钥、LLM Key

# 4. 创建种子数据（演示账号 + 家庭组）
python seed.py

# 5. 启动服务（默认 http://localhost:8000）
python -m app.main
# 或: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文档：http://localhost:8000/docs

### 端到端验证

```bash
cd backend
python verify.py
```

`verify.py` 使用 SQLite 临时数据库（路径通过 `tempfile.gettempdir()` 获取，兼容 Windows），不依赖 MySQL，覆盖 8 个关键步骤：注册 → 家庭组 → 发消息 → 草稿 → 确认分享（带最终 title/body）→ 收件箱 → 权限防火墙 → 非 family 成员 403。

## 演示账号

种子数据（`backend/seed.py`）与前端 `LoginPanel` 完全一致，一键"演示账号登录"即可使用：

| 用户名 | 密码 | 角色 |
|-------|------|------|
| demo_child | demo123456 | 孩子 |
| demo_parent | demo123456 | 家长 |
| demo_teacher | demo123456 | 老师 |

种子数据会自动创建孩子档案和家庭组（孩子 + 家长 + 老师）。

## 打包为 HTML Zip

```bash
npm run build
cd dist
zip -r ../translateme-dist.zip .
```

`vite.config.ts` 已配置 `base: './'`，使用相对资源路径，保证打包后的 HTML Zip 可通过本地静态服务器或社区上传环境正常打开。

## 部署

`dist/` 可直接部署到 GitHub Pages / Vercel / Netlify。

## 演示提示

- 首页选择身份后进入登录页，可点击"演示账号登录"一键体验，或"使用本地模式"不连后端
- 后端模式下：孩子发送 → 确认草稿（可编辑最终 title/body）→ 家长收件箱可见 → 家长回复 → 孩子收件箱可见
- 本地模式下：用模块级内存状态模拟三方收件箱，同一设备切换身份即可看到消息流
- 老师端为独立流程，不接收孩子消息（MVP 阶段）

## 隐私与权限

- **登录鉴权**：所有 API 需 JWT，未登录无法访问
- **统一权限校验**：PermissionService 校验孩子只能访问自己的档案，家长/老师只能访问同一家庭组的孩子
- **inbox 权限收紧**：传 `child_id` 时校验访问权限；不传时只返回当前用户可访问的孩子列表的 inbox，不能按 `to_role` 查全库
- **家庭组权限收紧**：创建家庭组仅 child 本人，添加/删除成员仅现有成员可操作；非家庭组用户无法把自己加入别人家庭组
- **孩子确认优先**：草稿确认接口支持孩子编辑后的最终 title/body，后端保存并发送确认版本；审计日志记录"孩子确认了最终发送版本"，不记录原始私密输入
- **安全事件接入后端**：后端返回 `safety_event_id` 时，前端安全卡选择分支会调用 `/safety/events/{id}/resolve`，由后端记录事件
- **敏感内容加密**：消息正文使用 AES-256-GCM 加密存储
- **LLM 文案对齐**：发送外部 LLM 时明确标注是"安全检测后的最小必要原文片段"，不伪称"脱敏摘要"
- 复制功能走浏览器原生 Clipboard API，不经过任何服务端
- 若部署到 GitHub Pages / Vercel / Netlify，托管平台可能产生基础访问日志，由平台方管理

## 仓库结构

```
TranslateMe/
├── src/                              # 前端
│   ├── App.tsx                       # 主界面 + 状态机（home/identity/login/chat）
│   ├── main.tsx                      # 入口
│   ├── styles.css                    # 完整视觉样式（移动优先）
│   ├── types.ts                      # 共享类型
│   ├── components/
│   │   ├── IdentitySelect.tsx        # 身份选择
│   │   ├── LoginPanel.tsx            # 登录/注册面板（含演示账号一键登录）
│   │   ├── CopyButton.tsx
│   │   ├── Footer.tsx                # 底部边界声明
│   │   └── chat/                     # 对话壳 + 各类卡片
│   ├── controllers/
│   │   ├── useChildController.ts     # 孩子端（默认走后端，失败回退本地）
│   │   ├── useParentController.ts    # 家长端（默认走后端）
│   │   └── useTeacherController.ts   # 老师端（默认走后端）
│   ├── lib/
│   │   ├── apiClient.ts              # 后端 API 客户端（auth/conversations/drafts/safety/llm/family）
│   │   ├── safety.ts                 # 前端安全确认检测（与后端并行）
│   │   ├── childBuilder.ts           # 孩子端澄清+草稿生成（本地回退）
│   │   ├── parentBuilder.ts          # 家长端通用建议+防火墙（本地回退）
│   │   ├── teacherBuilder.ts         # 老师端谈话建议（本地回退）
│   │   └── messageStore.ts           # 本地模拟收件箱（后端失败 fallback）
│   └── data/
│       └── examples.ts               # 三端示例输入
├── backend/                          # 后端
│   ├── app/
│   │   ├── main.py                   # FastAPI 入口
│   │   ├── config.py                 # 配置
│   │   ├── api/                      # 路由（auth/conversations/family/safety/memory/llm_routes/ws）
│   │   ├── core/                     # 安全/加密/LLM/权限/WS 管理
│   │   ├── db/models/                # SQLAlchemy 模型
│   │   ├── schemas/                  # Pydantic v2 schemas
│   │   └── services/                 # 业务服务（含 permission_service 统一权限校验）
│   ├── seed.py                       # 种子数据（演示账号 + 家庭组）
│   ├── verify.py                     # 端到端验证（SQLite 临时库，8 步）
│   ├── requirements.txt
│   ├── docker-compose.yml            # MySQL
│   └── .env.example
├── docs/
│   ├── project-brief.md              # 项目背景
│   ├── safety-boundary.md            # 安全边界（含 LLM 接入约束）
│   └── architecture.md               # 真实产品架构说明
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## 后续方向

当前已接入后端、登录、权限校验、AES 加密、安全事件记录。后续可继续完善：

- WebSocket 实时推送（多端在线同步收件箱）
- Alembic 数据库迁移管理
- 真正的脱敏/摘要 pipeline（替代当前"最小必要原文片段"）
- 更细粒度的家庭组角色与授权流转
- 学校心理老师/咨询师工作台

真实产品架构详见 [docs/architecture.md](docs/architecture.md)。
