import os
from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Bill
from utils.email import send_email

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# Placeholder data for bill portions
USER_BILLS = {
    'alice': 20.50,
    'bob': 35.00,
    'charlie': 15.75
}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('signin'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Please enter a username.'
    return render_template('signin.html', error=error)

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('signin'))
    entry = Bill.query.filter_by(username=username).first()
    if entry:
        bill = entry.amount
    else:
        bill = USER_BILLS.get(username.lower(), 0.0)
    return render_template('dashboard.html', username=username, bill=bill)

@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('signin'))
    return render_template('profile.html', username=username)


@app.route('/bill', methods=['GET', 'POST'])
def manage_bill():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        amount = float(request.form['amount'])
        bill = Bill.query.filter_by(username=username).first()
        action = 'updated' if bill else 'created'
        if not bill:
            bill = Bill(username=username, email=email, amount=amount)
            db.session.add(bill)
        else:
            bill.email = email
            bill.amount = amount
        db.session.commit()
        send_email(email, f'Bill {action}', 'emails/bill_notification.mjml', {
            'username': username,
            'amount': amount,
        })
        return redirect(url_for('dashboard'))
    return render_template('bill_form.html')

@app.route('/signout')
def signout():
    session.pop('username', None)
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)
