# FamilyPhonePay

This project is a simple Flask web application that allows users to sign in and view
their portion of a bill. It includes basic routes for signing in, viewing a dashboard,
and displaying a profile page.

## Setup

1. Install Python 3 and pip.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app.py
```

The application will start on `http://localhost:5000/`.

## Pages

- `/signin` – Sign in with a username.
- `/dashboard` – View your portion of the bill after signing in.
- `/profile` – Simple profile page showing the current username.

This project uses in-memory placeholder data for demonstration purposes only.

## Running Tests

To run the automated test suite locally:

```bash
pip install -r requirements.txt
pytest
```
