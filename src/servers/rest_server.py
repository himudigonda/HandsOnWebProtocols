from fastapi import Depends, FastAPI
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import ActivityLog, AsyncSessionLocal

app = FastAPI(title="REST Protocol Server")


# Dependency for DB Session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/logs")
async def get_logs(limit: int = 100):
    """Standard REST Endpoint: Returns a list of JSON objects"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ActivityLog).order_by(desc(ActivityLog.timestamp)).limit(limit)
        )
        logs = result.scalars().all()
        return logs


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rest"}


if __name__ == "__main__":
    import uvicorn

    # Run on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
