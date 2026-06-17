"""
FastAPI 应用入口
"""

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.session import init_db_sync
from app.api import auth, conversations, memory, safety, family, llm_routes, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：确保数据库表存在
    try:
        init_db_sync()
    except Exception as e:
        print(f"[WARNING] 数据库初始化失败: {e}")
    yield
    # 关闭
    pass


app = FastAPI(
    title="以孩子为中心的家庭组 AI 沟通中枢",
    description=(
        "一个围绕孩子的私密沟通系统。核心设计原则：\n"
        "1. 孩子的消息默认仅孩子本人和 AI 可以读取\n"
        "2. 对外分享需要孩子明确确认（降敏摘要级别）\n"
        "3. 家长/老师无法追问未授权的具体内容\n"
        "4. 高风险表达走独立的安全处理流程\n"
        "5. 所有操作都有审计日志"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(memory.router, prefix="/api/v1")
app.include_router(safety.router, prefix="/api/v1")
app.include_router(family.router, prefix="/api/v1")
app.include_router(llm_routes.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "child-centered-family-ai"}


@app.get("/")
async def root():
    return {
        "name": "以孩子为中心的家庭组 AI 沟通中枢",
        "version": "1.0.0",
        "health": "/health",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
