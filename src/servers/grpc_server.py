import asyncio
import grpc
from sqlalchemy import select, desc
from src.core.database import AsyncSessionLocal, ActivityLog

# Import generated code (ensure the compile step above ran!)
try:
    from src.servers.protos import logs_pb2, logs_pb2_grpc
except ImportError:
    print("❌ Error: Proto files not found. Did you run the compile command?")
    exit(1)

class ActivityService(logs_pb2_grpc.ActivityServiceServicer):
    async def GetLogs(self, request, context):
        limit = request.limit
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ActivityLog).order_by(desc(ActivityLog.timestamp)).limit(limit)
            )
            db_logs = result.scalars().all()

        # Convert to Proto Message
        response_logs = [
            logs_pb2.LogEntry(
                id=log.id,
                user_id=log.user_id,
                action=log.action,
                timestamp=str(log.timestamp),
                ip_address=log.ip_address,
                metadata_json=log.metadata_json if log.metadata_json else "" # Ensure metadata_json is not None
            ) for log in db_logs
        ]
        return logs_pb2.LogList(logs=response_logs)

async def serve():
    server = grpc.aio.server()
    logs_pb2_grpc.add_ActivityServiceServicer_to_server(ActivityService(), server)
    server.add_insecure_port('[::]:50051')
    print("🚀 gRPC Server starting on port 50051...")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
