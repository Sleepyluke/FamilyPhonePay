# FamilyPhonePay

This project is a simple Flask web application that allows users to sign in and view
bills. It now supports email notifications when bills are created or updated.

## Setup

1. Install Python 3 and pip.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set the following environment variables:

- `SENDGRID_API_KEY` – API key for sending mail.
- `EMAIL_FROM_ADDRESS` – Address used as the sender.
- `DATABASE_URL` – Optional SQLAlchemy database URI (defaults to `sqlite:///data.db`).

4. Run the application:

```bash
python app.py
```

The application will start on `http://localhost:5000/`.

## Pages

- `/signin` – Sign in with a username.
- `/dashboard` – View your portion of the bill after signing in.
- `/profile` – Simple profile page showing the current username.
- `/bill` – Create or update a bill (sends an email notification).

This project uses placeholder data for demonstration purposes only.
