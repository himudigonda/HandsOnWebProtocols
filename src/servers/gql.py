from typing import List

import strawberry
from fastapi import FastAPI
from sqlalchemy import desc, select
from strawberry.fastapi import GraphQLRouter

from src.core.database import AsyncSessionLocal, DBLog


@strawberry.type
class LogType:
    id: int
    user_id: int
    action: str
    timestamp: str
    ip_address: str
    metadata_json: str


@strawberry.type
class Query:
    @strawberry.field
    async def logs(self, limit: int = 100) -> List[LogType]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(DBLog).order_by(desc(DBLog.timestamp)).limit(limit)
            )
            data = result.scalars().all()
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
app = FastAPI(title="Arena GraphQL Server")
app.include_router(GraphQLRouter(schema), prefix="/graphql")


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
