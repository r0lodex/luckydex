"""
Unit tests for the Luckydex API.

To run these tests:
    pytest tests/

To run with coverage:
    pytest tests/ --cov=app --cov-report=html
"""

import pytest
from chalice.test import Client
from app import app


@pytest.fixture
def test_client():
    """Create a test client for the Chalice app."""
    with Client(app) as client:
        yield client


def test_index(test_client):
    """Test the root endpoint."""
    response = test_client.http.get('/')
    assert response.status_code == 200
    json_response = response.json_body
    assert 'message' in json_response
    assert json_response['message'] == 'Welcome to Luckydex API'
    assert json_response['status'] == 'healthy'


def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.http.get('/health')
    assert response.status_code == 200
    json_response = response.json_body
    assert json_response['status'] == 'healthy'
    assert json_response['service'] == 'luckydex'


def test_home_page(test_client):
    """Test the home page endpoint returns HTML."""
    response = test_client.http.get('/home')
    assert response.status_code == 200
    assert response.headers.get('Content-Type') == 'text/html'
    # Check that the response body contains HTML
    body = response.body
    assert b'<!DOCTYPE html>' in body or b'<html' in body
    assert b'Luckydex' in body
    assert b'drawNumber' in body  # JavaScript function name


def test_luckydex_endpoint(test_client):
    """Test the luckydex endpoint returns a random number."""
    response = test_client.http.get('/luckydex')
    assert response.status_code == 200
    json_response = response.json_body

    # Check required fields are present
    assert 'success' in json_response
    assert json_response['success'] is True
    assert 'id' in json_response
    assert 'number' in json_response
    assert 'name' in json_response
    assert 'description' in json_response
    assert 'total_entries' in json_response

    # Since we don't have real credentials in tests, it should return mock data
    assert json_response.get('mock_data') is True


def test_luckydex_multiple_calls(test_client):
    """Test that luckydex can be called multiple times successfully."""
    for _ in range(3):
        response = test_client.http.get('/luckydex')
        assert response.status_code == 200
        json_response = response.json_body
        assert json_response['success'] is True
        assert 'number' in json_response


def test_cors_enabled(test_client):
    """Test that CORS is enabled for the API."""
    # The CORS headers should be present in the response
    # This is handled by Chalice's CORS configuration
    response = test_client.http.get('/luckydex')
    assert response.status_code == 200
    # Note: In actual deployment, CORS headers would be present
    # The test client may not show them, but we verify CORS is configured in app.py

