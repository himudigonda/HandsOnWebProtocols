import asyncio
import time
import httpx
import grpc
from src.servers.protos import logs_pb2, logs_pb2_grpc
import statistics

# --- CONFIG ---
ITERATIONS = 100
LIMIT = 500 # Items to fetch per request

async def benchmark_rest():
    """Test REST API on Port 8000"""
    async with httpx.AsyncClient() as client:
        start = time.time()
        for _ in range(ITERATIONS):
            resp = await client.get(f"http://localhost:8000/logs?limit={LIMIT}")
            resp.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            assert len(resp.json()) == LIMIT
        duration = time.time() - start
        return duration

async def benchmark_graphql():
    """Test GraphQL API on Port 8001 - Requesting ONLY id and action"""
    query = """
    query {
        logs(limit: %d) {
            id
            action
        }
    }
    """ % LIMIT
    
    async with httpx.AsyncClient() as client:
        start = time.time()
        for _ in range(ITERATIONS):
            resp = await client.post("http://localhost:8001/graphql", json={"query": query})
            resp.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            data = resp.json()
            assert len(data["data"]["logs"]) == LIMIT
        duration = time.time() - start
        return duration

async def benchmark_grpc():
    """Test gRPC on Port 50051"""
    # Channel should be reused in real apps, but we include connect time for fairness
    start = time.time()
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = logs_pb2_grpc.ActivityServiceStub(channel)
        for _ in range(ITERATIONS):
            response = await stub.GetLogs(logs_pb2.GetLogsRequest(limit=LIMIT))
            assert len(response.logs) == LIMIT
    duration = time.time() - start
    return duration

async def run_benchmarks():
    print(f"🏎️  Starting Benchmarks ({ITERATIONS} reqs, {LIMIT} items each)...")
    # Ensure servers are running! (In a real CI pipeline we'd spawn them here)
    try:
        # 1. REST
        rest_time = await benchmark_rest()
        print(f"🔹 REST API:     {rest_time:.4f}s total | {rest_time/ITERATIONS*1000:.2f}ms per req")

        # 2. GraphQL
        gql_time = await benchmark_graphql()
        print(f"🔹 GraphQL:      {gql_time:.4f}s total | {gql_time/ITERATIONS*1000:.2f}ms per req (Partial Payload)")

        # 3. gRPC
        grpc_time = await benchmark_grpc()
        print(f"🔹 gRPC:         {grpc_time:.4f}s total | {grpc_time/ITERATIONS*1000:.2f}ms per req")

        print("\n🏆 Results Analysis:")
        if grpc_time < rest_time:
            print(f"   gRPC was {rest_time/grpc_time:.1f}x faster than REST")
        if gql_time < rest_time:
            print(f"   GraphQL was {rest_time/gql_time:.1f}x faster than REST (due to smaller payload)")

    except Exception as e:
        print(f"\n❌ Benchmark failed. Are servers running? Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
