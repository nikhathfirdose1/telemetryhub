from fastapi import APIRouter
from prometheus_client import Counter

router = APIRouter()
INGEST_REQUESTS = Counter(
    "telemetry_ingest_requests_total",
    "Total number of telemetry ingest requests",
    ["type"]
)

@router.get("/dry-run")
def dry_run():
    INGEST_REQUESTS.labels(type="metric").inc()
    return {"ok": True}
