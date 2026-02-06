import asyncio
import json
import random

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import func, select

from src.core.database import AsyncSessionLocal, DBLog

app = FastAPI(title="Arena WebSocket Server")


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # Wait for filter
        data = await websocket.receive_text()
        request_data = json.loads(data)
        action_filter = request_data.get("action_filter")

        async with AsyncSessionLocal() as session:
            max_id = await session.scalar(select(func.max(DBLog.id)))
            if not max_id:
                return

            while True:
                await asyncio.sleep(0.1)
                rand_id = random.randint(1, max_id)
                result = await session.execute(select(DBLog).where(DBLog.id == rand_id))
                log = result.scalar_one_or_none()

                if log and (not action_filter or log.action == action_filter):
                    payload = {"id": log.id, "user": log.user_id, "action": log.action}
                    await websocket.send_json(payload)
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
