import datetime
import os
import random
import sqlite3

# Constants
TOTAL_RECORDS = 1_000_000
DB_PATH = "./data/app.db"
BATCH_SIZE = 50_000

ACTIONS = [
    "LOGIN",
    "LOGOUT",
    "VIEW_PAGE",
    "CLICK_BUTTON",
    "SUBMIT_FORM",
    "DOWNLOAD_FILE",
]
IPS = ["192.168.1.1", "10.0.0.1", "172.16.0.1", "127.0.0.1", "8.8.8.8"]


def seed():
    print(f"🚀 Scaling to {TOTAL_RECORDS} records using optimized SQL batching...")

    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if not exists (minimal schema)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS user_activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        metadata_json TEXT,
        ip_address TEXT
    );
    """
    )

    # Optional: Clear existing to ensure exact scale
    # cursor.execute("DELETE FROM user_activity_logs")

    print(
        f"🌱 Current count: {cursor.execute('SELECT COUNT(*) FROM user_activity_logs').fetchone()[0]}"
    )

    records_to_add = TOTAL_RECORDS

    for i in range(0, records_to_add, BATCH_SIZE):
        batch = []
        for _ in range(min(BATCH_SIZE, records_to_add - i)):
            batch.append(
                (
                    random.randint(1, 1000),
                    random.choice(ACTIONS),
                    (
                        datetime.datetime.utcnow()
                        - datetime.timedelta(minutes=random.randint(0, 50000))
                    ).isoformat(),
                    '{"browser": "chrome", "os": "mac", "perf": "high"}',
                    random.choice(IPS),
                )
            )

        cursor.executemany(
            "INSERT INTO user_activity_logs (user_id, action, timestamp, metadata_json, ip_address) VALUES (?, ?, ?, ?, ?)",
            batch,
        )
        conn.commit()
        print(f"   Buffered {i + len(batch)} / {records_to_add}...", end="\r")

    print(
        f"\n✅ Successfully scaled database to {cursor.execute('SELECT COUNT(*) FROM user_activity_logs').fetchone()[0]} records!"
    )
    conn.close()


if __name__ == "__main__":
    seed()
