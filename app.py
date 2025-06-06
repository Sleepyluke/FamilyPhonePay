from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-key'


# In-memory data structures for bills
# Each bill contains an id, cycle_month, total, optional pdf path and per-user
# surcharge items
BILLS = []

def get_bill(bill_id):
    for bill in BILLS:
        if bill['id'] == bill_id:
            return bill
    return None

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
    cycle_month = None
    shares = {}
    if BILLS:
        bill = BILLS[-1]
        cycle_month = bill['cycle_month']
        participants = bill['items'].keys()
        if participants:
            base_share = bill['total'] / len(participants)
            for user in participants:
                surcharge = bill['items'].get(user, 0.0)
                shares[user] = base_share + surcharge
    return render_template('dashboard.html', username=username,
                           cycle_month=cycle_month, shares=shares)

@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('signin'))
    return render_template('profile.html', username=username)


@app.route('/api/bills', methods=['GET', 'POST'])
def api_bills():
    if request.method == 'POST':
        cycle_month = request.form.get('cycle_month') or request.json.get('cycle_month')
        total = request.form.get('total') or request.json.get('total')
        if not cycle_month or total is None:
            return jsonify({'error': 'cycle_month and total required'}), 400
        bill = {
            'id': len(BILLS) + 1,
            'cycle_month': cycle_month,
            'total': float(total),
            'pdf': None,
            'items': {}
        }
        BILLS.append(bill)
        return jsonify({'message': 'created', 'id': bill['id']}), 201
    return jsonify({'bills': BILLS})


@app.route('/api/bills/<int:bill_id>/items', methods=['POST'])
def api_bill_items(bill_id):
    bill = get_bill(bill_id)
    if not bill:
        return jsonify({'error': 'bill not found'}), 404
    username = request.form.get('username') or request.json.get('username')
    surcharge = request.form.get('surcharge') or request.json.get('surcharge')
    if username is None or surcharge is None:
        return jsonify({'error': 'username and surcharge required'}), 400
    bill['items'][username.lower()] = float(surcharge)
    return jsonify({'message': 'item updated', 'bill': bill})


@app.route('/bills/new', methods=['GET', 'POST'])
def create_bill():
    if request.method == 'POST':
        cycle_month = request.form.get('cycle_month')
        total = request.form.get('total')
        if cycle_month and total:
            bill = {
                'id': len(BILLS) + 1,
                'cycle_month': cycle_month,
                'total': float(total),
                'pdf': None,
                'items': {}
            }
            BILLS.append(bill)
            return redirect(url_for('edit_bill_items', bill_id=bill['id']))
    return render_template('create_bill.html')


@app.route('/bills/<int:bill_id>/items', methods=['GET', 'POST'])
def edit_bill_items(bill_id):
    bill = get_bill(bill_id)
    if not bill:
        return 'Bill not found', 404
    if request.method == 'POST':
        username = request.form.get('username')
        surcharge = request.form.get('surcharge')
        if username and surcharge is not None:
            bill['items'][username.lower()] = float(surcharge)
    return render_template('edit_items.html', bill_id=bill_id, items=bill['items'])

@app.route('/signout')
def signout():
    session.pop('username', None)
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)
