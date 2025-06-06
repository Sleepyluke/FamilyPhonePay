from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance used across the application
# It will be initialized in app.py

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))

    family = db.relationship('Family', back_populates='members')
    notifications = db.relationship('NotificationLog', back_populates='user')

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    members = db.relationship('User', back_populates='family')
    bills = db.relationship('Bill', back_populates='family')

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2))
    due_date = db.Column(db.Date)

    family = db.relationship('Family', back_populates='bills')
    items = db.relationship('BillItem', back_populates='bill')

class BillItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    description = db.Column(db.String(200))
    amount = db.Column(db.Numeric(10, 2))

    bill = db.relationship('Bill', back_populates='items')

class NotificationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')
