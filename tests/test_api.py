"""
Tests for the FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data
    assert data['status'] == 'healthy'
    print("✓ Health endpoint test passed")

def test_metadata_endpoint():
    """Test the metadata endpoint."""
    response = client.get("/metadata")
    
    assert response.status_code == 200
    data = response.json()
    assert 'brand' in data
    assert 'intents' in data
    assert 'num_intents' in data
    assert isinstance(data['intents'], list)
    print("✓ Metadata endpoint test passed")

def test_predict_endpoint_without_models():
    """Test predict endpoint when models aren't loaded."""
    response = client.post("/predict", json={"message": "Where is my order?"})
    
    # Should return 503 if models not loaded
    assert response.status_code in [200, 503]
    print("✓ Predict endpoint test passed")

def test_predict_endpoint_malformed_input():
    """Test predict endpoint with malformed input."""
    response = client.post("/predict", json={})
    
    assert response.status_code == 422  # Validation error
    print("✓ Malformed input test passed")

def test_examples_endpoint():
    """Test the examples endpoint."""
    response = client.get("/examples")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print("✓ Examples endpoint test passed")

if __name__ == "__main__":
    test_health_endpoint()
    test_metadata_endpoint()
    test_predict_endpoint_without_models()
    test_predict_endpoint_malformed_input()
    test_examples_endpoint()
    print("\nAll API tests passed!")
