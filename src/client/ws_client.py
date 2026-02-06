import asyncio
import websockets
import json

async def hello():
    uri = "ws://localhost:8003/ws"
    async with websockets.connect(uri) as websocket:
        # Send Filter
        await websocket.send(json.dumps({"action_filter": "LOGIN"}))
        
        # Read stream
        while True:
            response = await websocket.recv()
            print(f"< Received: {response}")

if __name__ == "__main__":
    asyncio.run(hello())
