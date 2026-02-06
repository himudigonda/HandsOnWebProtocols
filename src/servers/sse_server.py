import asyncio
import json
import random
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from src.core.database import AsyncSessionLocal, ActivityLog

app = FastAPI(title="SSE Stream Server")

async def fake_data_stream():
    """Generator that simulates real-time data arriving"""
    async with AsyncSessionLocal() as session:
        # Get max ID to pick random rows quickly
        max_id = await session.scalar(select(func.max(ActivityLog.id)))
        
        while True:
            # Simulate work/latency
            await asyncio.sleep(0.1) 
            
            # Pick a random row to push
            # Ensure max_id is not None and greater than 0
            if max_id is None or max_id == 0:
                print("No data in ActivityLog table. Waiting for data...")
                await asyncio.sleep(1) # Wait longer if no data
                continue

            rand_id = random.randint(1, max_id)
            result = await session.execute(select(ActivityLog).where(ActivityLog.id == rand_id))
            log = result.scalar_one_or_none()
            
            if log:
                data = {
                    "id": log.id,
                    "action": log.action,
                    "timestamp": str(log.timestamp)
                }
                # SSE Format: "data: <payload>

"
                yield f"data: {json.dumps(data)}

"

@app.get("/stream")
async def stream_logs():
    return StreamingResponse(fake_data_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    # Run on port 8002
    uvicorn.run(app, host="0.0.0.0", port=8002)
