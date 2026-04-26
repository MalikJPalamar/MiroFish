"""
conftest.py - Pytest configuration and fixtures for MiroFish backend tests.
"""
import pytest
import sys
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def mock_limiter_import():
    """
    Mock the Flask-Limiter to avoid initialization issues during test collection.

    The ratelimit module in app/ uses limiter = Limiter(...) with arguments
    that may not be compatible with all versions. This fixture prevents
    the actual Limiter initialization by mocking the module.
    """
    # Create mock limiter and RATE_LIMITS
    mock_limiter = MagicMock()
    mock_rate_limits = {
        "simulation_create": "5 per minute",
        "simulation_prepare": "3 per minute",
        "default": "100 per minute",
    }

    # Patch before any app imports happen
    with patch.dict('sys.modules', {
        'flask_limiter': MagicMock(),
        'flask_limiter.util': MagicMock(),
    }):
        yield


@pytest.fixture
def mock_config():
    """Mock the Config class for tests that need it."""
    with patch('app.config.Config') as mock:
        instance = MagicMock()
        instance.ZEP_API_KEY = "test_zep_key_12345"
        instance.OASIS_API_KEY = "test_oasis_key_12345"
        instance.OASIS_API_URL = "https://api.example.com"
        instance.OASIS_SIMULATION_DATA_DIR = "/tmp/simulations"
        mock.return_value = instance
        yield mock
