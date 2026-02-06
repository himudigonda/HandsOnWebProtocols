import asyncio
import json
import random

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select

from src.core.database import AsyncSessionLocal, DBLog

app = FastAPI(title="Arena SSE Server")


async def event_stream():
    """Simulate real-time events by picking random rows"""
    async with AsyncSessionLocal() as session:
        max_id = await session.scalar(select(func.max(DBLog.id)))
        if not max_id:
            yield 'data: {"error": "No data"}\n\n'
            return

        while True:
            await asyncio.sleep(0.1)
            rand_id = random.randint(1, max_id)
            result = await session.execute(select(DBLog).where(DBLog.id == rand_id))
            log = result.scalar_one_or_none()

            if log:
                data = {
                    "id": log.id,
                    "action": log.action,
                    "timestamp": str(log.timestamp),
                }
                yield f"data: {json.dumps(data)}\n\n"


@app.get("/stream")
async def stream():
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
