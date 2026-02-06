import asyncio
import random
import datetime
from src.core.database import AsyncSessionLocal, ActivityLog, init_db, engine

# Constants
TOTAL_RECORDS = 100_000
BATCH_SIZE = 1000

ACTIONS = ["LOGIN", "LOGOUT", "VIEW_PAGE", "CLICK_BUTTON", "SUBMIT_FORM", "DOWNLOAD_FILE"]
IPS = ["192.168.1.1", "10.0.0.1", "172.16.0.1", "127.0.0.1", "8.8.8.8"]

async def seed():
    print(f"🌱 Seeding database with {TOTAL_RECORDS} records...")
    
    # Ensure tables exist
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check current count
        # (Optional: delete existing? For now, we just append to simulate growth)
        
        batch = []
        for i in range(TOTAL_RECORDS):
            log = ActivityLog(
                user_id=random.randint(1, 1000),
                action=random.choice(ACTIONS),
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(minutes=random.randint(0, 10000)),
                metadata_json='{"browser": "chrome", "os": "mac"}',
                ip_address=random.choice(IPS)
            )
            batch.append(log)
            
            if len(batch) >= BATCH_SIZE:
                session.add_all(batch)
                await session.commit()
                batch = []
                print(f"   Inserted {i+1} records...", end="\r")
        
        if batch:
            session.add_all(batch)
            await session.commit()
            
    print(f"\n✅ Successfully seeded {TOTAL_RECORDS} records!")

if __name__ == "__main__":
    asyncio.run(seed())
