import pytest
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'CalFusion' in response.data

def test_add_icloud_page(client):
    response = client.get('/add_icloud_calendar')
    assert response.status_code == 200
    assert b'Apple ID' in response.data 