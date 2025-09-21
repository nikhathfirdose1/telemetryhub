from fastapi import FastAPI
from app.api import health, metrics, ingest
from app.config import APP_NAME



app = FastAPI(title=APP_NAME)
app.include_router(health.router, tags=["health"])
app.include_router(metrics.router, tags=["metrics"])
app.include_router(ingest.router,  prefix="/ingest", tags=["ingest"])