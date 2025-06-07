import os
import pytest
from datetime import datetime
from werkzeug.security import generate_password_hash

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import app  # noqa: F401
from app import app as flask_app
from models import db, User, Family, Bill, BillItem


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        db.create_all()
        family = Family(name='Smith')
        manager = User(
            username='manager',
            password_hash=generate_password_hash('pass'),
            role='manager',
            family=family,
        )
        member = User(
            username='alice',
            password_hash=generate_password_hash('pw'),
            role='user',
            family=family,
        )
        db.session.add_all([family, manager, member])
        db.session.commit()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()


def login(client, username='alice', password='pw'):
    return client.post('/signin', data={'username': username, 'password': password}, follow_redirects=True)


def test_dashboard_calculates_user_total(client):
    with flask_app.app_context():
        family = Family.query.first()
        manager = User.query.filter_by(username='manager').first()
        alice = User.query.filter_by(username='alice').first()
        bill = Bill(
            family_id=family.id,
            created_by=manager.id,
            total_amount=15,
            published_at=datetime.utcnow(),
        )
        db.session.add(bill)
        db.session.flush()
        db.session.add_all([
            BillItem(bill_id=bill.id, user_id=alice.id, description='cell', amount=10),
            BillItem(bill_id=bill.id, user_id=alice.id, description='addon', amount=5),
        ])
        db.session.commit()

    login(client)
    rv = client.get('/dashboard')
    assert rv.status_code == 200
    assert b'$15.00' in rv.data


def test_dashboard_no_bill(client):
    login(client)
    rv = client.get('/dashboard')
    assert rv.status_code == 200
    assert b'No bill available' in rv.data
