"""
数据库会话管理
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from app.config import settings
from app.db.base import Base


def get_sync_url():
    """将异步 URL 转换为同步 URL"""
    url = settings.DATABASE_URL
    if url.startswith("mysql+aiomysql://"):
        return url.replace("mysql+aiomysql://", "mysql+pymysql://", 1)
    return url


# 异步引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,
    pool_pre_ping=True,
    pool_size=settings.SQLALCHEMY_POOL_SIZE,
    max_overflow=10,
)

# 异步会话工厂
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db():
    """FastAPI 依赖注入用的会话生成器"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def init_db_sync():
    """同步初始化数据库（用于启动时创建表）"""
    sync_url = get_sync_url()
    engine = create_engine(sync_url, echo=settings.SQLALCHEMY_ECHO)

    # 导入所有模型以确保被注册到 Base.metadata
    import app.db.models.users
    import app.db.models.child_profiles
    import app.db.models.consents
    import app.db.models.family_groups
    import app.db.models.group_members
    import app.db.models.conversations
    import app.db.models.messages
    import app.db.models.drafts
    import app.db.models.share_permissions
    import app.db.models.inbox_messages
    import app.db.models.memory_items
    import app.db.models.safety_events
    import app.db.models.audit_logs
    import app.db.models.idempotency_keys

    # 创建表
    Base.metadata.create_all(engine)
    engine.dispose()
    print("数据库表初始化完成")
