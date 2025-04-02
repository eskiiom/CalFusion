import os
import pytest
from app import app as flask_app, db

@pytest.fixture(autouse=True)
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test.db",
        "SECRET_KEY": "test_secret_key",
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", "test_id"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", "test_secret"),
    })
    
    # Create the database and the database table
    with flask_app.app_context():
        db.create_all()
    
    yield flask_app
    
    # Clean up after the test
    with flask_app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Calendriers' in response.data

def test_add_icloud_page(client):
    response = client.get('/add_icloud_calendar')
    assert response.status_code == 200
    assert b'identifiant' in response.data.lower() or b'apple id' in response.data.lower()

def test_oauth2callback_without_code(client):
    response = client.get('/oauth2callback')
    assert response.status_code == 302  # Should redirect 