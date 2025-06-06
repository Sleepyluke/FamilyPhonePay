# FamilyPhonePay

This project is a simple Flask web application that allows users to sign in and view
their portion of a bill. It includes basic routes for signing in, viewing a dashboard,
and displaying a profile page. The application now uses SQLAlchemy for persistence
and includes instructions for running database migrations.

## Setup

1. Install Python 3 and pip.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and adjust the values if needed. By default the
   application uses `dev-secret` for `SECRET_KEY` and a SQLite database. To use
   another database you can set `DATABASE_URL` in `.env`. Example for PostgreSQL:

```bash
cp .env.example .env
echo "DATABASE_URL=postgresql://user:password@localhost/dbname" >> .env
```

4. Run database migrations (only required after the first setup or when models
   change). Initialize the migration repository once with `flask db init`, then
   use the provided make target to apply migrations:

```bash
flask db init        # only once
make migrate
```

5. Run the application using the make target:

```bash
make dev
```

The application will start on `http://localhost:5000/`.

## Pages

- `/signin` – Sign in with a username.
- `/dashboard` – View your portion of the bill after signing in.
- `/profile` – Simple profile page showing the current username.

This project uses in-memory placeholder data for demonstration purposes only.
