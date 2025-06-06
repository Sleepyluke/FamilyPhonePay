import os
import json
import pytest
from werkzeug.security import generate_password_hash

# set database to in-memory before importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import app
from app import app as flask_app
from models import db, User, Family, Bill, BillItem


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

