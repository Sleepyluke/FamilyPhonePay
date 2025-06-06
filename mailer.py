import os
import json
from urllib import request

SENDGRID_API_URL = 'https://api.sendgrid.com/v3/mail/send'


def send_email(to_email: str, subject: str, content: str) -> None:
    """Send a simple email via SendGrid."""
    api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('EMAIL_FROM')
    if not api_key or not from_email:
        raise RuntimeError('Email settings not configured')

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/plain", "value": content}],
    }
    data = json.dumps(payload).encode('utf-8')
    req = request.Request(
        SENDGRID_API_URL,
        data=data,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    # Perform request but ignore response content
    with request.urlopen(req) as resp:
        resp.read()
