from flask import Flask, request, jsonify
from models import db, Loan, Payment
from utils import calculate_interest, calculate_total_amount, calculate_emi

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/lend", methods=["POST"])
def lend():
    data = request.json
    P = data["loan_amount"]
    N = data["loan_period"]
    R = data["rate_of_interest"]
    customer_id = data["customer_id"]

    I = calculate_interest(P, N, R)
    A = calculate_total_amount(P, I)
    EMI = calculate_emi(A, N)

    loan = Loan(customer_id=customer_id, principal=P, interest=I,
                total_amount=A, emi=EMI, emi_months=N*12)
    db.session.add(loan)
    db.session.commit()
    return jsonify({
        "loan_id": loan.id,
        "total_amount": A,
        "emi": EMI
    })

@app.route("/payment", methods=["POST"])
def payment():
    data = request.json
    loan = Loan.query.get(data["loan_id"])
    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    amount = data["amount"]
    pay_type = data["type"].upper()
    
    payment = Payment(loan_id=loan.id, type=pay_type, amount=amount)
    db.session.add(payment)

    if pay_type == "EMI":
        loan.total_amount -= loan.emi
        loan.emi_months -= 1
    elif pay_type == "LUMPSUM":
        loan.total_amount -= amount
        reduced_months = int(amount / loan.emi)
        loan.emi_months = max(loan.emi_months - reduced_months, 0)

    db.session.commit()
    return jsonify({"message": "Payment successful"})

@app.route("/ledger/<loan_id>", methods=["GET"])
def ledger(loan_id):
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    payments = Payment.query.filter_by(loan_id=loan_id).all()
    transactions = [
        {"type": p.type, "amount": p.amount, "date": p.date.strftime("%Y-%m-%d")}
        for p in payments
    ]

    return jsonify({
        "loan_id": loan.id,
        "emi_amount": loan.emi,
        "emi_left": loan.emi_months,
        "balance_amount": round(loan.total_amount, 2),
        "transactions": transactions
    })

@app.route("/account/<customer_id>", methods=["GET"])
def account(customer_id):
    loans = Loan.query.filter_by(customer_id=customer_id).all()
    output = []
    for loan in loans:
        paid_amount = sum(p.amount for p in Payment.query.filter_by(loan_id=loan.id))
        output.append({
            "loan_id": loan.id,
            "principal": loan.principal,
            "interest": loan.interest,
            "total_amount": loan.principal + loan.interest,
            "emi_amount": loan.emi,
            "amount_paid": round(paid_amount, 2),
            "emi_left": loan.emi_months,
            "balance_amount": round(loan.total_amount, 2)
        })
    return jsonify(output)
