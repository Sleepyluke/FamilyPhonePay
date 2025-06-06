import os
import pytest
from werkzeug.security import generate_password_hash

# use in-memory database
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import app
from app import app as flask_app
from models import db, User

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        db.create_all()
        # create an existing user
        manager = User(
            username='manager',
            password_hash=generate_password_hash('pass'),
            role='manager',
        )
        db.session.add(manager)
        db.session.commit()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()


def test_register_new_user(client):
    rv = client.post('/register', data={'username': 'alice', 'password': 'pw'}, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Welcome, alice!' in rv.data
    with flask_app.app_context():
        assert User.query.filter_by(username='alice').first() is not None


def test_register_duplicate_username(client):
    # create existing user already done in fixture
    rv = client.post('/register', data={'username': 'manager', 'password': 'pass'}, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Username already taken.' in rv.data


def test_signin_success(client):
    rv = client.post('/signin', data={'username': 'manager', 'password': 'pass'}, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Welcome, manager!' in rv.data


def test_signin_invalid_password(client):
    rv = client.post('/signin', data={'username': 'manager', 'password': 'wrong'}, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Invalid username or password.' in rv.data
