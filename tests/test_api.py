import os
import json
import pytest
from werkzeug.security import generate_password_hash

# set database to in-memory before importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import app
from app import app as flask_app
from models import db, User, Family, Bill, BillItem, NotificationLog


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
