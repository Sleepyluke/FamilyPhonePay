from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance used across the application
# It will be initialized in app.py

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(50))
    auth_sub = db.Column(db.String(100))
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))

    family = db.relationship('Family', back_populates='members')
    notifications = db.relationship('NotificationLog', back_populates='user')
    bill_items = db.relationship('BillItem', back_populates='user')
    created_bills = db.relationship('Bill', back_populates='creator', foreign_keys='Bill.created_by')

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('User', back_populates='family')
    bills = db.relationship('Bill', back_populates='family')

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    cycle_month = db.Column(db.Integer)
    total_amount = db.Column(db.Numeric(10, 2))
    due_date = db.Column(db.Date)
    pdf_url = db.Column(db.String(255))
    published_at = db.Column(db.DateTime)

    family = db.relationship('Family', back_populates='bills')
    items = db.relationship('BillItem', back_populates='bill')
    notifications = db.relationship('NotificationLog', back_populates='bill')
    creator = db.relationship('User', back_populates='created_bills', foreign_keys=[created_by])

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String(200))
    amount = db.Column(db.Numeric(10, 2))
    is_recurring = db.Column(db.Boolean, default=False)

    bill = db.relationship('Bill', back_populates='items')
    user = db.relationship('User', back_populates='bill_items')

class NotificationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'))
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')
    bill = db.relationship('Bill', back_populates='notifications')
