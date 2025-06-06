# FamilyPhonePay

This project is a simple Flask web application that allows users to register,
log in, and view their portion of a bill. It uses **Flask-Login** for session
management and **SQLAlchemy** for persistence. Manager accounts can create
bills or invite new members.

## Setup

1. Install Python 3 and pip.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set the `DATABASE_URL` environment variable if you do not want to use the
   default SQLite database. Example for PostgreSQL:

```bash
export DATABASE_URL=postgresql://user:password@localhost/dbname
```

4. Run database migrations (only required after the first setup or when models
   change):

```bash
flask db init        # only once
flask db migrate -m "Initial tables"
flask db upgrade
```

5. Run the application:

```bash
python app.py
```

The application will start on `http://localhost:5000/`.

## Pages

- `/login` – Log in with your username and password.
- `/register` – Create a new account.
- `/dashboard` – View your portion of the bill after signing in.
- `/profile` – Simple profile page showing the current username.
- `/create_bill` – Manager-only page for creating a bill.
- `/invite` – Manager-only page for inviting members.

This project uses in-memory placeholder data for demonstration purposes only.
