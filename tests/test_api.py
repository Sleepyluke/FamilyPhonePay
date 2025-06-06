import os
import json
import pytest
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer

# set database to in-memory before importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import app
from app import app as flask_app
from models import db, User, Family, Bill, BillItem, NotificationLog, Invitation


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        db.create_all()
        manager = User(
            username='manager',
            password_hash=generate_password_hash('pass'),
            role='manager',
        )
        family = Family(name='Smith')
        db.session.add_all([manager, family])
        db.session.commit()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()


def login(client):
    return client.post('/signin', data={'username': 'manager', 'password': 'pass'}, follow_redirects=True)


def test_get_bill_detail(client):
    with flask_app.app_context():
        manager = User.query.filter_by(username='manager').first()
        family = Family.query.first()
        bill = Bill(family_id=family.id, created_by=manager.id, total_amount=100)
        db.session.add(bill)
        db.session.commit()
        bill_id = bill.id
        db.session.add(BillItem(bill_id=bill_id, description='test item', amount=10))
        db.session.commit()

    login(client)
    rv = client.get(f'/api/bills/{bill_id}')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['id'] == bill_id
    assert len(data['items']) == 1
    assert data['items'][0]['description'] == 'test item'



def test_publish_bill_sends_emails(client, monkeypatch):
    sent = []

    def fake_send(to_email, subject, body):
        sent.append((to_email, subject, body))

    monkeypatch.setattr('api.send_email', fake_send)

    with flask_app.app_context():
        family = Family.query.first()
        member = User(
            username='alice',
            password_hash=generate_password_hash('pw'),
            email='alice@example.com',
            family_id=family.id,
        )
        db.session.add(member)
        db.session.commit()
        fam_id = family.id

    login(client)
    rv = client.post('/api/bills', json={'family_id': fam_id})
    assert rv.status_code == 201
    assert len(sent) == 1
    assert sent[0][0] == 'alice@example.com'

    with flask_app.app_context():
        log = NotificationLog.query.filter_by(user_id=member.id).first()
        assert log is not None


def test_create_invitation(client, monkeypatch):
    sent = []

    def fake_send(to_email, subject, body):
        sent.append((to_email, subject, body))

    monkeypatch.setattr('api.send_email', fake_send)

    with flask_app.app_context():
        family = Family.query.first()
        fam_id = family.id

    login(client)
    rv = client.post('/api/invite', json={'email': 'new@example.com', 'family_id': fam_id})
    assert rv.status_code == 201
    assert len(sent) == 1
    assert sent[0][0] == 'new@example.com'

    with flask_app.app_context():
        inv = Invitation.query.filter_by(email='new@example.com').first()
        assert inv is not None


def test_accept_invitation(client):
    with flask_app.app_context():
        family = Family.query.first()
        serializer = URLSafeTimedSerializer(flask_app.secret_key)
        token = serializer.dumps('bob@example.com')
        inv = Invitation(family_id=family.id, email='bob@example.com', token=token)
        db.session.add(inv)
        db.session.commit()

    rv = client.post(f'/invite/{token}', data={'username': 'bob', 'password': 'pw'}, follow_redirects=True)
    assert rv.status_code == 200
    assert b'Welcome, bob!' in rv.data

    with flask_app.app_context():
        user = User.query.filter_by(username='bob').first()
        inv = Invitation.query.filter_by(token=token).first()
        assert user is not None
        assert user.email == 'bob@example.com'
        assert inv.accepted_at is not None
