import asyncio
import random
import json
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import AsyncSessionLocal, ActivityLog, init_db

# Configuration
NUM_LOGS_TO_GENERATE = 5000
BATCH_SIZE = 1000

# Possible values for log entries
ACTIONS = ["LOGIN", "LOGOUT", "VIEW_ITEM", "ADD_TO_CART", "PURCHASE", "UPDATE_PROFILE"]
IP_PREFIXES = ["192.168.1.", "10.0.0.", "172.16.0."]

async def generate_random_log() -> ActivityLog:
    user_id = random.randint(1, 10000) # 10,000 unique users
    action = random.choice(ACTIONS)
    timestamp = datetime.datetime.utcnow() - datetime.timedelta(seconds=random.randint(0, 3600*24*30)) # Last 30 days
    metadata_json = json.dumps({"item_id": random.randint(100, 9999)} if "ITEM" in action or "CART" in action else {})
    ip_address = random.choice(IP_PREFIXES) + str(random.randint(1, 254))
    
    return ActivityLog(
        user_id=user_id,
        action=action,
        timestamp=timestamp,
        metadata_json=metadata_json,
        ip_address=ip_address
    )

async def seed_database():
    print("🚀 Initializing database and creating tables...")
    await init_db() # Ensure tables are created

    print(f"Generating {NUM_LOGS_TO_GENERATE} user activity logs...")
    
    async with AsyncSessionLocal() as session:
        logs_to_add = []
        for i in range(1, NUM_LOGS_TO_GENERATE + 1):
            log = await generate_random_log()
            logs_to_add.append(log)

            if i % BATCH_SIZE == 0:
                session.add_all(logs_to_add)
                await session.commit()
                print(f"  Added {i} logs to the database...")
                logs_to_add = []
        
        # Add any remaining logs
        if logs_to_add:
            session.add_all(logs_to_add)
            await session.commit()
            print(f"  Added {NUM_LOGS_TO_GENERATE} logs to the database. Done.")

if __name__ == "__main__":
    asyncio.run(seed_database())
