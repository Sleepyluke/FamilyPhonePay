import os
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_migrate import Migrate
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'


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

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


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

if __name__ == '__main__':
    app.run(debug=True)
