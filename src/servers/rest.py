from typing import List

from fastapi import Depends, FastAPI
from sqlalchemy import desc, select

from src.core.database import AsyncSessionLocal, DBLog
from src.core.models import LogEntry

app = FastAPI(title="Arena REST Server")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/logs", response_model=List[LogEntry])
async def get_logs(limit: int = 100):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(DBLog).order_by(desc(DBLog.timestamp)).limit(limit)
        )
        return result.scalars().all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
