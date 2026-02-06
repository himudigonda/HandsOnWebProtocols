import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import select, func
from src.core.database import AsyncSessionLocal, ActivityLog

app = FastAPI(title="WebSocket Server")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Client connected")
    
    try:
        # 1. Wait for client to send a filter message
        # Example message from client: {"action_filter": "LOGIN"}
        data = await websocket.receive_text()
        request_data = json.loads(data)
        action_filter = request_data.get("action_filter")
        
        print(f"🔎 Filtering stream for: {action_filter}")

        # 2. Start the stream based on filter
        async with AsyncSessionLocal() as session:
            max_id = await session.scalar(select(func.max(ActivityLog.id)))
            
            while True:
                await asyncio.sleep(0.1) # Simulate real-time delay
                
                # Pick random ID
                # Ensure max_id is not None and greater than 0
                if max_id is None or max_id == 0:
                    print("No data in ActivityLog table. Waiting for data...")
                    await asyncio.sleep(1) # Wait longer if no data
                    continue

                rand_id = random.randint(1, max_id)
                result = await session.execute(select(ActivityLog).where(ActivityLog.id == rand_id))
                log = result.scalar_one_or_none()
                
                # Only send if it matches filter (Simulating server-side processing)
                if log and (not action_filter or log.action == action_filter):
                    payload = {
                        "id": log.id,
                        "user": log.user_id,
                        "action": log.action
                    }
                    await websocket.send_json(payload)

    except WebSocketDisconnect:
        print("❌ Client disconnected")
    except Exception as e:
        print(f"Error in websocket_endpoint: {e}")

if __name__ == "__main__":
    import uvicorn
    # Run on port 8003
    uvicorn.run(app, host="0.0.0.0", port=8003)
