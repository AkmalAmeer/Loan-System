from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Loan(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = db.Column(db.String, nullable=False)
    principal = db.Column(db.Float, nullable=False)
    interest = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    emi = db.Column(db.Float, nullable=False)
    emi_months = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.String, db.ForeignKey('loan.id'), nullable=False)
    type = db.Column(db.String)  # EMI / LUMPSUM
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.utcnow)
