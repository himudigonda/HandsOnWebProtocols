-- data/schema.sql
-- Schema for User Activity Logs

CREATE TABLE IF NOT EXISTS user_activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata_json TEXT, -- Storing JSON as TEXT
    ip_address TEXT
);

CREATE INDEX IF NOT EXISTS idx_user_id ON user_activity_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON user_activity_logs (timestamp);
