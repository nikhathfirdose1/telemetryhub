import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

APP_NAME: str = os.getenv("APP_NAME", "TelemetryHub")

# We'll use these very soon when we add Postgres/Redis
DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")  
REDIS_URL: Optional[str] = os.getenv("REDIS_URL")        
