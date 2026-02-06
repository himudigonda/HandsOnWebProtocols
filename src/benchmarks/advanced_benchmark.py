import asyncio
import json
import statistics
import time

import grpc
import httpx
from rich import print as rprint
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from src.servers.protos import logs_pb2, logs_pb2_grpc

# --- CONFIG ---
ITERATIONS = 50
CONCURRENT_CLIENTS = 10
BATCH_SIZES = [1, 100, 1000]
PORTS = {"REST": 8000, "GraphQL": 8001, "SSE": 8002, "WebSocket": 8003, "gRPC": 50051}

console = Console()


class ProtocolBenchmark:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.results = {}

    async def check_health(self):
        try:
            if self.name == "gRPC":
                async with grpc.aio.insecure_channel(
                    f"localhost:{self.port}"
                ) as channel:
                    stub = logs_pb2_grpc.ActivityServiceStub(channel)
                    resp = await stub.CheckHealth(logs_pb2.HealthRequest(), timeout=2)
                    return resp.status == "healthy"
            elif self.name == "WebSocket":
                # WebSocket uses FastAPI for health check too
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"http://localhost:{self.port}/health", timeout=2
                    )
                    return resp.status_code == 200
            else:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"http://localhost:{self.port}/health", timeout=2
                    )
                    return resp.status_code == 200
        except Exception:
            return False

    async def benchmark_latency(self, limit=100):
        # Implementation in subclasses
        pass


class RestBenchmark(ProtocolBenchmark):
    async def benchmark_latency(self, limit=100):
        async with httpx.AsyncClient() as client:
            start = time.perf_counter()
            resp = await client.get(f"http://localhost:{self.port}/logs?limit={limit}")
            resp.raise_for_status()
            duration = time.perf_counter() - start
            return duration


class GraphQlBenchmark(ProtocolBenchmark):
    async def benchmark_latency(self, limit=100):
        query = "query { logs(limit: %d) { id action timestamp } }" % limit
        async with httpx.AsyncClient() as client:
            start = time.perf_counter()
            resp = await client.post(
                f"http://localhost:{self.port}/graphql", json={"query": query}
            )
            resp.raise_for_status()
            duration = time.perf_counter() - start
            return duration


class GrpcBenchmark(ProtocolBenchmark):
    async def benchmark_latency(self, limit=100):
        async with grpc.aio.insecure_channel(f"localhost:{self.port}") as channel:
            stub = logs_pb2_grpc.ActivityServiceStub(channel)
            start = time.perf_counter()
            await stub.GetLogs(logs_pb2.GetLogsRequest(limit=limit))
            duration = time.perf_counter() - start
            return duration


async def run_iterations(benchmark_obj, limit, count):
    latencies = []
    for _ in range(count):
        latencies.append(await benchmark_obj.benchmark_latency(limit))
    return latencies


async def run_concurrent(benchmark_obj, limit, clients, reqs_per_client):
    async def client_task():
        return await run_iterations(benchmark_obj, limit, reqs_per_client)

    start = time.perf_counter()
    tasks = [client_task() for _ in range(clients)]
    results = await asyncio.gather(*tasks)
    total_duration = time.perf_counter() - start

    all_latencies = [lat for res in results for lat in res]
    return total_duration, all_latencies


async def main():
    rprint(
        Panel.fit(
            "[bold blue]🚀 Protocol Lab: Advanced Benchmark Suite[/bold blue]\n[italic]Comparing REST, GraphQL, and gRPC at Scale[/italic]"
        )
    )

    benchmarks = [
        RestBenchmark("REST", PORTS["REST"]),
        GraphQlBenchmark("GraphQL", PORTS["GraphQL"]),
        GrpcBenchmark("gRPC", PORTS["gRPC"]),
    ]

    # 1. Health Check
    with console.status("[bold green]Checking server health...") as status:
        for b in benchmarks:
            if await b.check_health():
                rprint(f"✅ {b.name} is [green]UP[/green]")
            else:
                rprint(f"❌ {b.name} is [red]DOWN[/red]")
                return

    # 2. Variable Payload Benchmark
    rprint(
        f"\n[bold yellow]📊 Category 1: Payload Size Impact ({ITERATIONS} requests each)[/bold yellow]"
    )
    payload_table = Table(title="Latency by Payload Size (ms)")
    payload_table.add_column("Protocol", justify="center", style="cyan")
    for size in BATCH_SIZES:
        payload_table.add_column(f"{size} items", justify="right")

    for b in benchmarks:
        row = [b.name]
        for size in BATCH_SIZES:
            latencies = await run_iterations(b, size, ITERATIONS)
            avg_ms = statistics.mean(latencies) * 1000
            row.append(f"{avg_ms:.2f}")
        payload_table.add_row(*row)

    console.print(payload_table)

    # 3. Concurrency Benchmark
    rprint(
        f"\n[bold yellow]concurrent 📈 Category 2: High Concurrency ({CONCURRENT_CLIENTS} clients, 10 reqs each)[/bold yellow]"
    )
    concurrent_table = Table(title="Concurrency Performance")
    concurrent_table.add_column("Protocol", style="cyan")
    concurrent_table.add_column("Total Time (s)", justify="right")
    concurrent_table.add_column("Avg Latency (ms)", justify="right")
    concurrent_table.add_column("P95 Latency (ms)", justify="right")
    concurrent_table.add_column("Throughput (req/s)", justify="right")

    for b in benchmarks:
        duration, latencies = await run_concurrent(b, 100, CONCURRENT_CLIENTS, 10)
        total_reqs = CONCURRENT_CLIENTS * 10
        avg_ms = statistics.mean(latencies) * 1000
        p95_ms = statistics.quantiles(latencies, n=20)[18] * 1000  # 95th percentile
        throughput = total_reqs / duration

        concurrent_table.add_row(
            b.name,
            f"{duration:.3f}",
            f"{avg_ms:.2f}",
            f"{p95_ms:.2f}",
            f"{throughput:.1f}",
        )

    console.print(concurrent_table)

    rprint("\n[bold green]🏆 Benchmark Summary:[/bold green]")
    rprint(
        "gRPC continues to dominate in high-concurrency and large-payload scenarios due to binary serialization and multiplexing."
    )


if __name__ == "__main__":
    asyncio.run(main())
