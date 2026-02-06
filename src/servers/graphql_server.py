import strawberry
from fastapi import FastAPI
from sqlalchemy import desc, select
from strawberry.fastapi import GraphQLRouter

from src.core.database import ActivityLog, AsyncSessionLocal


# 1. Define the GraphQL Type (Schema)
@strawberry.type
class LogType:
    id: int
    user_id: int  # Changed from str to int based on ActivityLog model
    action: str
    timestamp: str
    ip_address: str
    metadata_json: str


# 2. Define the Resolver
@strawberry.type
class Query:
    @strawberry.field
    async def logs(self, limit: int = 100) -> list[LogType]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ActivityLog).order_by(desc(ActivityLog.timestamp)).limit(limit)
            )
            data = result.scalars().all()
            # Convert SQLAlchemy models to Strawberry Types
            return [
                LogType(
                    id=d.id,
                    user_id=d.user_id,
                    action=d.action,
                    timestamp=str(d.timestamp),
                    ip_address=d.ip_address,
                    metadata_json=d.metadata_json,
                )
                for d in data
            ]


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="GraphQL Server")
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "graphql"}


if __name__ == "__main__":
    import uvicorn

    # Run on port 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)
