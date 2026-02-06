from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LogEntry(BaseModel):
    id: Optional[int] = None
    user_id: int
    action: str
    timestamp: datetime
    ip_address: str
    metadata_json: str  # Heavy payload simulation

    class Config:
        from_attributes = True
