import pytest
from app import app


def test_signin_required():
    tester = app.test_client()
    response = tester.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/signin' in response.headers['Location']


def test_user_bill_display():
    tester = app.test_client()
    with tester:
        tester.post('/signin', data={'username': 'alice'}, follow_redirects=True)
        response = tester.get('/dashboard')
        assert b"$20.50" in response.data
