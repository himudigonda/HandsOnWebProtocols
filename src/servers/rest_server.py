from fastapi import FastAPI, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import AsyncSessionLocal, ActivityLog

app = FastAPI(title="REST Protocol Server")

# Dependency for DB Session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/logs")
async def get_logs(limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Standard REST Endpoint: Returns a list of JSON objects"""
    result = await db.execute(
        select(ActivityLog).order_by(desc(ActivityLog.timestamp)).limit(limit)
    )
    logs = result.scalars().all()
    return logs

if __name__ == "__main__":
    import uvicorn
    # Run on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
