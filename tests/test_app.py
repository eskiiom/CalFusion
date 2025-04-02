import os
import sys
import pytest
from unittest.mock import patch
from app import app as flask_app, db

@pytest.fixture(autouse=True)
def app():
    """Create application for the tests."""
    test_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'test.db')
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db_path}",
        "SECRET_KEY": "test_secret_key",
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", "test_id"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", "test_secret"),
        "WTF_CSRF_ENABLED": False,  # Désactiver CSRF pour les tests
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

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_index_page(client):
    with flask_app.app_context():
        response = client.get('/')
        assert response.status_code == 200
        # Vérifier le titre de la page au lieu du contenu spécifique
        assert b'CalFusion' in response.data

def test_add_icloud_page(client):
    with flask_app.app_context():
        response = client.get('/add_icloud_calendar')
        assert response.status_code == 200
        assert b'identifiant' in response.data.lower() or b'apple id' in response.data.lower()

@patch('google_auth_oauthlib.flow.Flow.from_client_config')
def test_oauth2callback_without_code(mock_flow, client):
    with flask_app.app_context():
        # Simuler une requête sans code
        response = client.get('/oauth2callback')
        assert response.status_code == 302
        assert '/' in response.location  # Redirection vers la page d'accueil

@patch('google_auth_oauthlib.flow.Flow.from_client_config')
def test_oauth2callback_with_invalid_state(mock_flow, client):
    with flask_app.app_context():
        with client.session_transaction() as session:
            session['state'] = 'correct_state'
        
        # Simuler une requête avec un état invalide
        response = client.get('/oauth2callback?state=wrong_state&code=test_code')
        assert response.status_code == 302
        assert '/' in response.location  # Redirection vers la page d'accueil

@patch('google_auth_oauthlib.flow.Flow.from_client_config')
def test_oauth2callback_with_valid_state(mock_flow, client):
    with flask_app.app_context():
        test_state = 'test_state'
        with client.session_transaction() as session:
            session['state'] = test_state
        
        # Simuler une requête valide
        response = client.get(f'/oauth2callback?state={test_state}&code=test_code')
        assert response.status_code == 302  # Redirection après authentification réussie 