import asyncio
import json

import httpx
import websockets
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

console = Console()


async def listen_sse():
    console.print("[bold yellow]📡 Listening to SSE Log Stream...[/bold yellow]")
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://localhost:8002/stream") as response:
            count = 0
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    count += 1
                    data = json.loads(line[6:])
                    console.print(f"[dim]SSE {count:03d}:[/dim] {data}")
                    if count >= 10:
                        break


async def listen_ws():
    console.print("\n[bold cyan]🔌 Connecting to WebSocket Log Stream...[/bold cyan]")
    uri = "ws://localhost:8003/ws"
    async with websockets.connect(uri) as websocket:
        # Send filter
        filter_msg = {"action_filter": "SUBMIT_FORM"}
        await websocket.send(json.dumps(filter_msg))
        console.print(f"🔎 Sent filter: {filter_msg}")

        count = 0
        while count < 10:
            message = await websocket.recv()
            count += 1
            data = json.loads(message)
            console.print(f"[dim]WS  {count:03d}:[/dim] {data}")


async def main():
    console.print(Panel.fit("[bold green]Interactive Protocol Lab Demo[/bold green]"))
    try:
        await listen_sse()
        await listen_ws()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    asyncio.run(main())
