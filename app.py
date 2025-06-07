import os
import json
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    Response,
    stream_with_context,
)
from flask_migrate import Migrate, upgrade
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, Invitation, Family, Bill, BillItem, NotificationLog
from api import api_bp
from events import add_listener, remove_listener, send_event
from mailer import send_email

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'


app.register_blueprint(api_bp)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Placeholder data for bill portions
USER_BILLS = {
    'alice': 20.50,
    'bob': 35.00,
    'charlie': 15.75
}

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('signin'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            error = 'Username and password are required.'
        elif User.query.filter_by(username=username).first():
            error = 'Username already taken.'
        else:
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                role='user',
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('register.html', error=error)


@app.route('/invite/<token>', methods=['GET', 'POST'])
def accept_invite(token):
    invite = Invitation.query.filter_by(token=token).first_or_404()
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            error = 'Username and password are required.'
        elif User.query.filter_by(username=username).first():
            error = 'Username already taken.'
        else:
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=invite.email,
                role='user',
                family_id=invite.family_id,
            )
            db.session.add(user)
            invite.accepted_at = datetime.utcnow()
            db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('accept_invite.html', error=error, email=invite.email)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        error = 'Invalid username or password.'
    return render_template('signin.html', error=error)

@app.route('/dashboard')
@login_required
def dashboard():
    bill = USER_BILLS.get(current_user.username.lower(), 0.0)
    return render_template('dashboard.html', bill=bill)


@app.route('/events')
@login_required
def sse_events():
    q = add_listener()

    def stream(q):
        try:
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        except GeneratorExit:
            remove_listener(q)

    return Response(stream_with_context(stream(q)), mimetype="text/event-stream")

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/add-item', methods=['GET', 'POST'])
@login_required
def add_item():
    if not current_user.family_id:
        abort(400)
    family = Family.query.get(current_user.family_id)
    members = family.members
    error = None
    if request.method == 'POST':
        description = request.form.get('description')
        if not description:
            error = 'Description required.'
        else:
            amounts = {}
            total = 0
            for m in members:
                amt_str = request.form.get(f'amount_{m.id}', '0')
                try:
                    amt = float(amt_str)
                except ValueError:
                    amt = 0
                if amt > 0:
                    amounts[m.id] = amt
                    total += amt
            if not amounts:
                error = 'At least one amount is required.'

        if not error:
            bill = Bill(
                family_id=family.id,
                created_by=current_user.id,
                total_amount=total,
                published_at=datetime.utcnow(),
            )
            db.session.add(bill)
            db.session.commit()
            for uid, amt in amounts.items():
                item = BillItem(
                    bill_id=bill.id,
                    user_id=uid,
                    description=description,
                    amount=amt,
                )
                db.session.add(item)
            db.session.commit()
            subject = 'New bill item added'
            for uid in amounts:
                member = User.query.get(uid)
                if member.email:
                    try:
                        send_email(member.email, subject, description)
                    except Exception:
                        pass
                db.session.add(
                    NotificationLog(user_id=member.id, bill_id=bill.id, message=subject)
                )
            db.session.commit()
            send_event(json.dumps({'amount': float(total)}))
            return redirect(url_for('dashboard'))
    return render_template('add_item.html', error=error, members=members)


@app.route('/manage')
@login_required
def manage():
    if current_user.role != 'manager':
        return abort(403)
    return render_template('manage.html')

@app.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('signin'))

@app.route('/run-migrations')
def run_migrations():
    upgrade()
    return "Migrations applied!"

if __name__ == '__main__':
    app.run(debug=True)
