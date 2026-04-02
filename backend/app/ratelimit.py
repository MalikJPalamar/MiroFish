"""
Rate Limiting Configuration

Provides centralized rate limiting configuration for the MiroFish API.
Supports both in-memory and Redis storage backends.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create limiter instance (will be initialized with app in create_app)
limiter = Limiter(
    key_func=get_remote_address,
    app=None,  # Deferred initialization
    default_limits=["100 per minute"],
    storage_uri="memory://",
    strategy="fixed-window",
    add_headers=True,
    headers_enabled=True,
)

# Rate limit definitions
RATE_LIMITS = {
    # Default rate limit for most endpoints
    "default": "100 per minute",
    
    # Stricter limits for simulation-intensive operations
    # These trigger expensive LLM calls or heavy computations
    "simulation_create": "10 per minute",
    "simulation_prepare": "5 per minute",
    "simulation_run": "5 per minute",
    "simulation_generate_profiles": "10 per minute",
    "simulation_interview": "30 per minute",
    "simulation_interview_batch": "10 per minute",
    "simulation_interview_all": "5 per minute",
    "simulation_env": "30 per minute",
    
    # Health check and static endpoints - no rate limiting
    "exempt": None,
}


def init_limiter(app):
    """
    Initialize the limiter with the Flask app.
    
    Args:
        app: Flask application instance
    """
    limiter.init_app(app)
