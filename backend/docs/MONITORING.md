# MiroFish Backend Monitoring Guide

This document describes the monitoring and observability features available in the MiroFish backend.

## Health Check Endpoint

### GET /health

Returns the health status of the service along with system resource usage.

**Response:**
```json
{
  "status": "ok",
  "service": "MiroFish Backend",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "checks": {
    "memory": "ok",
    "cpu": "ok"
  },
  "details": {
    "memory_percent": 65.5,
    "cpu_percent": 12.3,
    "process_memory_mb": 256.45,
    "process_threads": 8
  }
}
```

**Status Values:**
- `ok`: All systems healthy
- `degraded`: Some resources are elevated (memory > 75% or CPU > 75%)
- `unhealthy`: Critical resource levels (memory > 90% or CPU > 90%)

### Kubernetes Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5001
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 5001
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## Prometheus Metrics Endpoint

### GET /metrics

Returns Prometheus-formatted metrics for scraping.

**Response Content-Type:** `text/plain; version=0.0.4; charset=utf-8`

### Available Metrics

#### Request Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `mirofish_request_latency_seconds` | Histogram | method, endpoint, status_code | Request latency in seconds |
| `mirofish_requests_total` | Counter | method, endpoint, status_code | Total request count |
| `mirofish_requests_in_progress` | Gauge | method, endpoint | Currently processing requests |

**Latency Buckets:** 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0 seconds

#### Simulation Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `mirofish_active_simulations` | Gauge | platform | Currently active simulations (twitter/reddit) |
| `mirofish_simulation_events_total` | Counter | event_type | Total simulation events (start/end/error/created) |

#### Error Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `mirofish_errors_total` | Counter | method, endpoint, error_type | Total errors (client_error: 4xx, server_error: 5xx) |

---

## Prometheus Configuration

Add the following job to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'mirofish-backend'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s
```

### Example prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'mirofish-backend'
    static_configs:
      - targets: ['mirofish-backend:5001']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

---

## Grafana Dashboard

A pre-configured Grafana dashboard is available at `grafana/dashboard.json`.

### Importing the Dashboard

1. Open Grafana
2. Click "+" > "Import"
3. Upload `grafana/dashboard.json` or paste its contents
4. Select the Prometheus data source
5. Click "Import"

### Dashboard Panels

The dashboard includes:

- **Request Rate**: Requests per second by endpoint
- **Latency P50/P95/P99**: Request latency percentiles
- **Error Rate**: Error percentage over time
- **Active Simulations**: Current simulation count by platform
- **Request In Progress**: Currently processing requests
- **CPU/Memory Usage**: System resource utilization
- **Top Endpoints by Latency**: Highest latency endpoints
- **Error Breakdown**: Client vs server errors

---

## Structured Logging

The backend supports structured JSON logging for production environments.

### Enabling JSON Logging

Set the environment variable:
```bash
export USE_JSON_LOGGING=true
```

### Log Format

```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "level": "INFO",
  "logger": "mirofish.api.simulation",
  "message": "创建模拟成功",
  "module": "simulation",
  "function": "create_simulation",
  "line": 226,
  "extra_fields": {
    "simulation_id": "sim_abc123",
    "project_id": "proj_xyz"
  }
}
```

### Log Fields

| Field | Description |
|-------|-------------|
| `timestamp` | ISO 8601 timestamp in UTC |
| `level` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `logger` | Logger name (e.g., `mirofish.api.simulation`) |
| `message` | Log message |
| `module` | Source module name |
| `function` | Function name |
| `line` | Line number in source |
| `exception` | Exception traceback (if applicable) |
| `extra_fields` | Additional structured data |

---

## Alerting Rules

### Example Prometheus Alerting Rules

```yaml
groups:
  - name: mirofish
    rules:
      # High Error Rate
      - alert: MiroFishHighErrorRate
        expr: |
          sum(rate(mirofish_errors_total[5m])) /
          sum(rate(mirofish_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate in MiroFish Backend"
          description: "Error rate is {{ $value | humanizePercentage }}"

      # Service Down
      - alert: MiroFishBackendDown
        expr: up{job="mirofish-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MiroFish Backend is down"
          description: "MiroFish backend has been down for more than 1 minute"

      # High Latency
      - alert: MiroFishHighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(mirofish_request_latency_seconds_bucket[5m])) by (le)
          ) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency"
          description: "P95 latency is {{ $value }}s"

      # No Active Simulations
      - alert: MiroFishNoActiveSimulations
        expr: sum(mirofish_active_simulations) == 0
        for: 30m
        labels:
          severity: info
        annotations:
          summary: "No active simulations"
          description: "There have been no active simulations for 30 minutes"
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_JSON_LOGGING` | `false` | Enable structured JSON logging |
| `FLASK_HOST` | `0.0.0.0` | Host to bind to |
| `FLASK_PORT` | `5001` | Port to bind to |
| `FLASK_DEBUG` | `True` | Enable debug mode |

---

## Health Check Integration

### Docker Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/health || exit 1
```

### Docker Compose

```yaml
services:
  mirofish-backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

---

## Troubleshooting

### Metrics Not Showing

1. Ensure prometheus-client is installed: `pip install prometheus-client>=0.19.0`
2. Check that /metrics endpoint is accessible
3. Verify Prometheus is configured with correct scrape target

### Health Check Failing

1. Check memory and CPU usage on the host
2. Review logs for exceptions during health check
3. Ensure psutil is installed: `pip install psutil>=5.9.0`

### High Cardinality Metrics

Endpoint paths with IDs are normalized automatically:
- `/api/simulation/sim_abc123` becomes `/api/simulation/:id`
- UUIDs and numeric IDs are replaced with `:id` placeholder
