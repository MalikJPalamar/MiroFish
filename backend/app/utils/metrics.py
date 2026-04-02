"""
Prometheus metrics for MiroFish backend
Provides request latency, request count, active simulations, and error rate metrics
"""

import time
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import request, Response


# Request latency histogram - buckets optimized for web requests
REQUEST_LATENCY = Histogram(
    'mirofish_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint', 'status_code'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# Request count by endpoint
REQUEST_COUNT = Counter(
    'mirofish_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status_code']
)

# Active simulations gauge
ACTIVE_SIMULATIONS = Gauge(
    'mirofish_active_simulations',
    'Number of currently active/running simulations',
    ['platform']
)

# Error rate counter
ERROR_COUNT = Counter(
    'mirofish_errors_total',
    'Total error count',
    ['method', 'endpoint', 'error_type']
)

# Simulation events counter
SIMULATION_EVENTS = Counter(
    'mirofish_simulation_events_total',
    'Total simulation events',
    ['event_type']
)

# Request in progress gauge
REQUESTS_IN_PROGRESS = Gauge(
    'mirofish_requests_in_progress',
    'Number of requests currently being processed',
    ['method', 'endpoint']
)


class MetricsMiddleware:
    """Flask middleware for collecting Prometheus metrics"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app"""
        self.app = app
        
        @app.before_request
        def before_request():
            """Record request start time"""
            request._start_time = time.time()
            endpoint = self._normalize_endpoint(request.path)
            REQUESTS_IN_PROGRESS.labels(method=request.method, endpoint=endpoint).inc()
        
        @app.after_request
        def after_request(response):
            """Record request metrics after response"""
            # Skip metrics endpoint itself
            if request.path == '/metrics':
                return response
            
            # Calculate latency
            start_time = getattr(request, '_start_time', None)
            if start_time is not None:
                latency = time.time() - start_time
                endpoint = self._normalize_endpoint(request.path)
                
                # Record latency
                REQUEST_LATENCY.labels(
                    method=request.method,
                    endpoint=endpoint,
                    status_code=response.status_code
                ).observe(latency)
                
                # Record request count
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=endpoint,
                    status_code=response.status_code
                ).inc()
                
                # Record errors (4xx and 5xx)
                if response.status_code >= 400:
                    error_type = 'client_error' if response.status_code < 500 else 'server_error'
                    ERROR_COUNT.labels(
                        method=request.method,
                        endpoint=endpoint,
                        error_type=error_type
                    ).inc()
            
            # Decrement in-progress counter
            endpoint = self._normalize_endpoint(request.path)
            REQUESTS_IN_PROGRESS.labels(method=request.method, endpoint=endpoint).dec()
            
            return response
    
    def _normalize_endpoint(self, path: str) -> str:
        """Normalize endpoint path to avoid high cardinality"""
        # Keep static paths as-is
        if path in ['/health', '/metrics', '/favicon.ico']:
            return path
        
        # Normalize API paths with IDs (replace UUIDs/numbers with placeholder)
        import re
        # Replace UUIDs
        normalized = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', ':id', path)
        # Replace numeric IDs
        normalized = re.sub(r'/\d+', '/:id', normalized)
        
        return normalized


def track_simulation_start(platform: str = 'both'):
    """Track simulation start event"""
    if platform in ['twitter', 'both']:
        ACTIVE_SIMULATIONS.labels(platform='twitter').inc()
    if platform in ['reddit', 'both']:
        ACTIVE_SIMULATIONS.labels(platform='reddit').inc()
    SIMULATION_EVENTS.labels(event_type='start').inc()


def track_simulation_end(platform: str = 'both'):
    """Track simulation end event"""
    if platform in ['twitter', 'both']:
        ACTIVE_SIMULATIONS.labels(platform='twitter').dec()
    if platform in ['reddit', 'both']:
        ACTIVE_SIMULATIONS.labels(platform='reddit').dec()
    SIMULATION_EVENTS.labels(event_type='end').inc()


def track_simulation_error(platform: str = 'both'):
    """Track simulation error event"""
    if platform in ['twitter', 'both']:
        ACTIVE_SIMULATIONS.labels(platform='twitter').dec()
    if platform in ['reddit', 'both']:
        ACTIVE_SIMULATIONS.labels(platform='reddit').dec()
    SIMULATION_EVENTS.labels(event_type='error').inc()


def track_simulation_create():
    """Track simulation creation event"""
    SIMULATION_EVENTS.labels(event_type='created').inc()


def get_metrics():
    """Generate Prometheus metrics output"""
    return generate_latest(), CONTENT_TYPE_LATEST


def metrics_endpoint():
    """Flask endpoint handler for /metrics"""
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )
