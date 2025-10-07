import pytest
import json
import sys
import os

# Add src directory to path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index route returns the HTML page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Vending Machine Test Interface' in response.data

def test_vend_route_valid_slot(client):
    """Test vending with valid slot IDs (1-5)."""
    for slot_id in range(1, 6):
        response = client.post(f'/vend/{slot_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'command_sent'
        assert data['slot'] == slot_id
        assert 'message' in data

def test_vend_route_invalid_slot(client):
    """Test vending with invalid slot IDs."""
    invalid_slots = [0, 6, 10, -1]
    
    for slot_id in invalid_slots:
        response = client.post(f'/vend/{slot_id}')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['slot'] == slot_id
        assert 'Invalid slot ID' in data['message']

def test_status_route(client):
    """Test the status endpoint."""
    response = client.get('/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'online'
    assert 'message' in data

def test_vend_route_non_integer_slot(client):
    """Test vending with non-integer slot values."""
    response = client.post('/vend/abc')
    assert response.status_code == 404  # Flask returns 404 for invalid int conversion