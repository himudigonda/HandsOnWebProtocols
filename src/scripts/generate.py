import asyncio
import datetime
import os
import random

from sqlalchemy.ext.asyncio import create_async_engine

from src.core.database import DATABASE_URL, Base, DBLog

# Config
ROWS = 100_000
BATCH = 5000

ACTIONS = ["LOGIN", "VIEW", "CLICK", "BUY", "LOGOUT", "ERROR"]


async def seed():
    print(f"🌊 Generating {ROWS} rows...")
    engine = create_async_engine(DATABASE_URL)

    # Ensure data directory exists
    os.makedirs("./data", exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        for i in range(0, ROWS, BATCH):
            data = []
            for _ in range(BATCH):
                data.append(
                    {
                        "user_id": random.randint(1, 5000),
                        "action": random.choice(ACTIONS),
                        "timestamp": datetime.datetime.now(),
                        "ip_address": f"10.0.{random.randint(0,255)}.{random.randint(0,255)}",
                        "metadata_json": '{"payload": "heavy"}'
                        * 5,  # ~100 bytes padding
                    }
                )
            await conn.execute(DBLog.__table__.insert(), data)
            print(f"Inserted {i+BATCH}...", end="\r")
            await conn.commit()
    print("\n✅ Database Hydrated.")


if __name__ == "__main__":
    asyncio.run(seed())
