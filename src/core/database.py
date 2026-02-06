import datetime
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./data/app.db"

Base = declarative_base()

class ActivityLog(Base):
    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    metadata_json = Column(String) # Storing JSON as TEXT
    ip_address = Column(String)

    def __repr__(self):
        return f"<ActivityLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"

# Async Engine and Session Local
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def init_db():
    async with engine.begin() as conn:
        # Create tables from schema.sql if not exists
        # Note: We are using a declarative base, so Base.metadata.create_all is more idiomatic
        # However, the project plan explicitly mentions schema.sql, so we'll simulate that for now
        # For a more robust solution, consider Alembic migrations
        await conn.run_sync(Base.metadata.create_all)

