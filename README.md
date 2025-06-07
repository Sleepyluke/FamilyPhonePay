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

## 🚀 Deploying to Render

Follow these steps to deploy on [Render](https://render.com):

1. **Setup a PostgreSQL Database**  
   Create a Postgres instance in Render and note the `DATABASE_URL`.

2. **Create an Environment Group**  
   Add the following variables to a new Environment Group and link it to your service:

   | Key | Value (example) |
   | --- | --------------- |
   | `SECRET_KEY` | a long random string |
   | `DATABASE_URL` | Render-provided Postgres URL |
   | `SENDGRID_API_KEY` | from your SendGrid dashboard |
   | `EMAIL_FROM` | a verified SendGrid sender email |

3. **Add a Temporary Migration Route**  
   Render doesn't provide shell access before the first deploy. Temporarily add this route to `app.py`:

   ```python
   @app.route('/run-migrations')
   def run_migrations():
       from flask_migrate import upgrade
       try:
           upgrade()
           return "✅ Migrations applied"
       except Exception as e:
           return f"❌ Migration failed: {e}", 500
   ```

   Deploy, then visit `/run-migrations` once to apply the migrations. Remove the route afterward.

4. **Switch to a Production Mailer**  
   Update `mailer.py` to use your SendGrid settings:

   ```diff
   -        sg = SendGridAPIClient()
   -        from_email = FROM_EMAIL or 'noreply@example.com'
   -        message = Mail(from_email=from_email, to_emails=[recipient], subject=subject, html_content=html)
   -        sg.send(message)
   +        sg = SendGridAPIClient(SENDGRID_API_KEY)
   +        from_email = EMAIL_FROM
   +        message = Mail(from_email=from_email, to_emails=[recipient], subject=subject, html_content=html)
   +        sg.send(message)
   ```

   Ensure `SENDGRID_API_KEY` and `EMAIL_FROM` are set in Render.

5. Render will use the `Procfile` to start the app. The included command runs migrations and then launches Gunicorn:

   ```bash
   web: bash -c "flask db upgrade && gunicorn -b 0.0.0.0:$PORT app:app"
   ```

   Gunicorn listens on the port provided by Render via the `$PORT` environment variable.

## Pages

- `/signin` – Sign in with a username.
- `/dashboard` – View your portion of the bill after signing in.
- `/profile` – Simple profile page showing the current username.

This project uses in-memory placeholder data for demonstration purposes only.
