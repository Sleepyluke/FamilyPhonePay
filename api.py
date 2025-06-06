from datetime import datetime
from flask import Blueprint, request, jsonify, abort
import json
from flask_login import login_required, current_user

from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from models import db, Family, Bill, BillItem, NotificationLog, Invitation
from mailer import send_email
from events import send_event

api_bp = Blueprint('api', __name__, url_prefix='/api')


def manager_required():
    if not current_user.is_authenticated or current_user.role != 'manager':
        abort(403)


@api_bp.route('/families', methods=['POST'])
@login_required
def create_family():
    manager_required()
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name required'}), 400
    family = Family(name=name)
    db.session.add(family)
    db.session.commit()
    return jsonify({'id': family.id, 'name': family.name}), 201


@api_bp.route('/invite', methods=['POST'])
@login_required
def create_invite():
    manager_required()
    data = request.get_json() or {}
    email = data.get('email')
    family_id = data.get('family_id')
    if not email or not family_id:
        return jsonify({'error': 'email and family_id required'}), 400

    serializer = URLSafeTimedSerializer(current_app.secret_key)
    token = serializer.dumps(email)
    invite = Invitation(family_id=family_id, email=email, token=token)
    db.session.add(invite)
    db.session.commit()

    link = f"{request.url_root.rstrip('/')}/invite/{token}"
    subject = 'You are invited'
    body = f'Please join by visiting {link}'
    try:
        send_email(email, subject, body)
    except Exception:
        pass
    return jsonify({'id': invite.id}), 201


@api_bp.route('/bills', methods=['POST'])
@login_required
def publish_bill():
    manager_required()
    data = request.get_json() or {}
    family_id = data.get('family_id')
    if not family_id:
        return jsonify({'error': 'family_id required'}), 400
    bill = Bill(
        family_id=family_id,
        created_by=current_user.id,
        cycle_month=data.get('cycle_month'),
        total_amount=data.get('total_amount'),
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
        published_at=datetime.utcnow(),
    )
    db.session.add(bill)
    db.session.commit()
    # notify family members
    family = Family.query.get(family_id)
    subject = 'New bill available'
    body = f'Bill #{bill.id} has been published.'
    for member in family.members:
        if member.email:
            try:
                send_email(member.email, subject, body)
            except Exception:
                pass
        log = NotificationLog(user_id=member.id, bill_id=bill.id, message=subject)
        db.session.add(log)
    db.session.commit()

    send_event(json.dumps({'amount': float(bill.total_amount or 0)}))

    return jsonify({'id': bill.id}), 201


@api_bp.route('/bills/<int:bill_id>/items', methods=['POST'])
@login_required
def add_surcharge(bill_id):
    manager_required()
    bill = Bill.query.get_or_404(bill_id)
    data = request.get_json() or {}
    description = data.get('description')
    amount = data.get('amount')
    if not description or amount is None:
        return jsonify({'error': 'description and amount required'}), 400
    item = BillItem(
        bill_id=bill.id,
        user_id=data.get('user_id'),
        description=description,
        amount=amount,
        is_recurring=data.get('is_recurring', False),
    )
    db.session.add(item)
    db.session.commit()

    send_event(json.dumps({'amount': float(bill.total_amount or 0)}))
    return jsonify({'id': item.id}), 201


@api_bp.route('/bills/<int:bill_id>', methods=['GET'])
@login_required
def bill_info(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    items = [
        {
            'id': item.id,
            'description': item.description,
            'amount': float(item.amount) if item.amount is not None else None,
            'user_id': item.user_id,
        }
        for item in bill.items
    ]
    return jsonify(
        {
            'id': bill.id,
            'family_id': bill.family_id,
            'total_amount': float(bill.total_amount) if bill.total_amount is not None else None,
            'due_date': bill.due_date.isoformat() if bill.due_date else None,
            'items': items,
        }
    )

