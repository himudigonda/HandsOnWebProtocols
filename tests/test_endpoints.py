import grpc
import httpx
import pytest

from src.servers.protos import logs_pb2, logs_pb2_grpc


@pytest.mark.asyncio
async def test_rest_health():
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://localhost:8000/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_graphql_health():
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://localhost:8001/health")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_grpc_health():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = logs_pb2_grpc.ActivityServiceStub(channel)
        resp = await stub.CheckHealth(logs_pb2.HealthRequest())
        assert resp.status == "healthy"


@pytest.mark.asyncio
async def test_rest_logs():
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://localhost:8000/logs?limit=5")
        assert resp.status_code == 200
        assert len(resp.json()) == 5
