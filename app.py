from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-key'

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
    bill = USER_BILLS.get(username.lower(), 0.0)
    return render_template('dashboard.html', username=username, bill=bill)

@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('signin'))
    return render_template('profile.html', username=username)

@app.route('/signout')
def signout():
    session.pop('username', None)
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)
