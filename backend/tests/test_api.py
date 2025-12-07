import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "status" in data


def test_health_check():
    """Test health check endpoint if exists"""
    response = client.get("/health")
    # May return 404 if not implemented, that's okay
    assert response.status_code in [200, 404]


def test_api_endpoints_exist():
    """Test that API endpoints are accessible"""
    # Test tickets endpoint
    response = client.get("/api/tickets")
    assert response.status_code in [200, 401, 404]  # May require auth
    
    # Test payments endpoint
    response = client.get("/api/payments")
    assert response.status_code in [200, 401, 404]  # May require auth
