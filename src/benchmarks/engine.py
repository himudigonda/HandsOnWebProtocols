import asyncio
import time

import grpc
import httpx
import pandas as pd
import websockets

from src.servers.protos import logs_pb2, logs_pb2_grpc


class BenchmarkEngine:
    async def run_latency_test(self, protocol, port, n=50):
        """Category 1: Latency (Sequential Requests)"""
        results = []

        for _ in range(n):
            start = time.perf_counter_ns()
            success = await self._make_request(protocol, port)
            end = time.perf_counter_ns()
            if success:
                results.append((end - start) / 1_000_000)  # to ms

        return pd.DataFrame(results, columns=["Latency (ms)"])

    async def run_throughput_test(self, protocol, port, duration_sec=3):
        """Category 2: Throughput (RPS)"""
        start_time = time.time()
        count = 0

        # REST and GraphQL use HTTP
        if protocol in ["REST", "GraphQL"]:
            async with httpx.AsyncClient() as client:
                while time.time() - start_time < duration_sec:
                    tasks = [
                        self._make_request(protocol, port, client) for _ in range(20)
                    ]
                    results = await asyncio.gather(*tasks)
                    count += sum(1 for r in results if r)

        elif protocol == "gRPC":
            async with grpc.aio.insecure_channel(f"localhost:{port}") as ch:
                stub = logs_pb2_grpc.ActivityServiceStub(ch)
                while time.time() - start_time < duration_sec:
                    tasks = [
                        stub.GetLogs(logs_pb2.GetLogsRequest(limit=1))
                        for _ in range(20)
                    ]
                    try:
                        await asyncio.gather(*tasks)
                        count += 20
                    except:
                        pass

        return count / duration_sec

    async def _make_request(self, protocol, port, client=None):
        try:
            if protocol == "REST":
                c = client or httpx.AsyncClient()
                resp = await c.get(f"http://localhost:{port}/logs?limit=1", timeout=2)
                if not client:
                    await c.aclose()
                return resp.status_code == 200
            elif protocol == "gRPC":
                async with grpc.aio.insecure_channel(f"localhost:{port}") as ch:
                    stub = logs_pb2_grpc.ActivityServiceStub(ch)
                    await stub.GetLogs(logs_pb2.GetLogsRequest(limit=1), timeout=2)
                return True
            elif protocol == "GraphQL":
                c = client or httpx.AsyncClient()
                q = "{ logs(limit: 1) { id } }"
                resp = await c.post(
                    f"http://localhost:{port}/graphql", json={"query": q}, timeout=2
                )
                if not client:
                    await c.aclose()
                return resp.status_code == 200
            return False
        except Exception as e:
            # print(f"Request failed: {e}")
            return False
