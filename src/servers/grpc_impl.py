import asyncio

import grpc
from sqlalchemy import desc, select

from src.core.database import AsyncSessionLocal, DBLog
from src.servers.protos import logs_pb2, logs_pb2_grpc


class ActivityService(logs_pb2_grpc.ActivityServiceServicer):
    async def CheckHealth(self, request, context):
        return logs_pb2.HealthResponse(status="healthy")

    async def GetLogs(self, request, context):
        limit = request.limit
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(DBLog).order_by(desc(DBLog.timestamp)).limit(limit)
            )
            db_logs = result.scalars().all()

        response_logs = [
            logs_pb2.LogEntry(
                id=log.id,
                user_id=log.user_id,
                action=log.action,
                timestamp=str(log.timestamp),
                ip_address=log.ip_address,
                metadata_json=log.metadata_json if log.metadata_json else "",
            )
            for log in db_logs
        ]
        return logs_pb2.LogList(logs=response_logs)


async def serve():
    server = grpc.aio.server()
    logs_pb2_grpc.add_ActivityServiceServicer_to_server(ActivityService(), server)
    server.add_insecure_port("[::]:50051")
    print("🚀 Arena gRPC Server starting on port 50051...")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
