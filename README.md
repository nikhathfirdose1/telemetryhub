# TelemetryHub

TelemetryHub is a production-grade observability backend that ingests high-volume telemetry (metrics & logs), detects anomalies, clusters errors, and surfaces actionable insights through Prometheus + Grafana dashboards and clean FastAPI endpoints.

## Highlights
- **Fast, typed APIs** (FastAPI) for ingest & query with interactive Swagger docs.
- **Durable storage** (PostgreSQL via SQLAlchemy) optimized for time-series queries.
- **Async pipelines** (Celery + Redis) for windowed aggregations, anomaly detection, and log clustering.
- **AI-assisted operations**: LLM-driven log clustering & summarization to cut alert noise and speed diagnosis.
- **First-class observability**: `/metrics` Prometheus exporter for infra + domain KPIs; Grafana dashboards for latency, throughput, error rates, and anomalies.
- **Batteries included**: Docker Compose stack, environment-based configuration, and a clean repository layout.

## Architecture
```
Clients ──▶ FastAPI (ingest & query)
              │
              ├──▶ PostgreSQL (metrics, logs, anomalies, clusters)
              ├──▶ Celery/Redis (windowed jobs, anomaly detection, AI clustering)
              └──▶ /metrics (Prometheus exporter)
                          │
                          └──▶ Prometheus TSDB ──▶ Grafana dashboards & alerts
```

## Data Model (Core Tables)
- **metric_events**: `(id, service, metric, value, ts, labels JSONB)`
- **log_events**: `(id, service, level, message, ts, context JSONB)`
- **anomalies**: `(id, service, metric, window, score, threshold, ts, model_version)`
- **log_clusters**: `(cluster_id, signature, summary, support_count, sample_messages[], ts_range, model_version)`

> Indexed on `(service, metric, ts)` and `(service, level, ts)` for efficient recent queries; partitions by day for scale.

## API Surface (Examples)
- **Health**
  - `GET /` → service heartbeat
- **Metrics Ingest & Query**
  - `POST /ingest/metrics` → JSON body: `{service, metric, value, ts, labels?}`
  - `GET /query/metrics?service=svc&metric=latency_ms&since=...&limit=...`
- **Logs Ingest & Query**
  - `POST /ingest/logs` → `{service, level, message, ts, context?}`
  - `GET /query/logs?service=svc&level=ERROR&since=...&limit=...`
- **Anomalies**
  - `GET /anomalies?service=svc&metric=latency_ms&since=...`
- **Diagnostics**
  - `GET /metrics` → Prometheus exporter (infra + domain counters/histograms)

All endpoints are documented at **`/docs`** with examples and schemas.

## AI in TelemetryHub
- **Log clustering & summarization**: Background jobs group similar errors across services and produce concise, de-duplicated summaries (signature + explanation + top examples). This reduces alert noise and directs engineers to the most informative failures first.
- **Anomaly detection**: Windowed jobs compute statistical features (e.g., rolling mean/std, seasonality) and score windows with ML (IsolationForest) to flag regressions early. Results link back to raw events for one-click drill-down.
- **Human-in-the-loop**: Feedback on clusters/anomalies updates stored thresholds and promotes better prompts/heuristics for future runs.

## Metrics (Prometheus)
- **Infra**: process CPU/mem, GC, request count, request latency.
- **Domain**:
  - `telemetry_ingest_requests_total{type="metric|log"}`
  - `telemetry_ingest_latency_seconds` (histogram)
  - `telemetry_anomalies_total{service,metric}`
  - `telemetry_log_clusters_total{service}`
These power Grafana panels for RPS, p95/p99 latency, error/log volume, anomaly rates, and top clusters.

## Dashboards (Grafana)
- **Service Health**: uptime, RPS, p95/p99 latency, 4xx/5xx rate
- **Ingestion**: throughput per service/metric; queue depth; worker success/failures
- **Anomalies**: counts by service/metric; top offenders; trend over time
- **Log Intelligence**: cluster count, summaries, support sizes; recent examples

## Quick Start (Local Dev)
```bash
git clone <your-ssh-or-https-url>
cd telemetryhub

python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **API Docs:** http://localhost:8000/docs  
- **OpenAPI JSON:** http://localhost:8000/openapi.json  
- **Prometheus Metrics:** http://localhost:8000/metrics

## Quick Start (Docker Compose)
```bash
docker compose up --build
# API:        http://localhost:8000
# Swagger:    http://localhost:8000/docs
# Postgres:   localhost:5432
# Redis:      localhost:6379
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000  (admin / admin)
```

## Example Usage
Ingest a metric:
```bash
curl -X POST :8000/ingest/metrics   -H "Content-Type: application/json"   -d '{"service":"payments","metric":"latency_ms","value":183,"ts":"2025-09-20T10:00:00Z","labels":{"env":"dev"}}'
```
Ingest a log:
```bash
curl -X POST :8000/ingest/logs   -H "Content-Type: application/json"   -d '{"service":"payments","level":"ERROR","message":"db timeout acquiring connection","ts":"2025-09-20T10:01:00Z","context":{"pool":"write"}}'
```
Query recent metrics:
```bash
curl ":8000/query/metrics?service=payments&metric=latency_ms&limit=50"
```

## Configuration
Environment variables (see `.env.example`):
- `APP_NAME` – display name for docs/UI.
- `DATABASE_URL` – Postgres connection string.
- `REDIS_URL` – Redis broker/backend for Celery.
- `OPENAI_API_KEY` or similar – if you enable LLM log clustering.

## Repository Layout
```
app/
  api/             # routers: health, metrics, ingest, query, anomalies
  utils/           # db engine/session, models, metrics helpers
  main.py          # FastAPI app bootstrap
worker/
  celery_app.py    # Celery initialization
  tasks.py         # async jobs (aggregation, anomalies, AI clustering)
configs/           # Prometheus & Grafana configs (compose mounts)
tests/             # pytest suites
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

## Security & Reliability
- Stateless API with idempotent ingestion and consistent error shapes.
- Structured logging with request IDs for traceability.
- Principle-of-least-privilege DB roles and environment-based config.

## License
MIT
