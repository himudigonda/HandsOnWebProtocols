import os

from sqlalchemy import Column, DateTime, Integer, String, Text, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

DB_PATH = "./data/arena.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

Base = declarative_base()


class DBLog(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    action = Column(String)
    timestamp = Column(DateTime, index=True)
    ip_address = Column(String)
    metadata_json = Column(Text)


engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_stats():
    """Returns row count for dashboard verification"""
    if not os.path.exists(DB_PATH):
        return 0
    try:
        async with AsyncSessionLocal() as session:
            return await session.scalar(select(func.count()).select_from(DBLog))
    except Exception:
        return 0


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
