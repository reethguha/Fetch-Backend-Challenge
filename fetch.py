from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize App
app = Flask(__name__)

# Initialize Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///points.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Table for keeping track of transactions
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payer = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

# Table for keeping track of balance
class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payer = db.Column(db.String(50), unique=True, nullable=False)
    points = db.Column(db.Integer, nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Routes
# Add points to database
@app.route('/add', methods=['POST'])
def add_points():
    data = request.json
    payer = data['payer']
    points = data['points']
    timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

    # Add transaction
    transaction = Transaction(payer=payer, points=points, timestamp=timestamp)
    db.session.add(transaction)

    # Update payer balance
    balance = Balance.query.filter_by(payer=payer).first()
    if not balance:
        balance = Balance(payer=payer, points=0)
        db.session.add(balance)
    balance.points += points

    db.session.commit()
    return "", 200

# Spend points
@app.route('/spend', methods=['POST'])
def spend_points():
    data = request.json
    points_to_spend = data['points']

    # Check if user has enough points
    total_points = db.session.query(db.func.sum(Balance.points)).scalar() or 0
    if total_points < points_to_spend:
        return "Not enough points.", 400

    # Sort transactions by timestamp (oldest first)
    transactions = Transaction.query.order_by(Transaction.timestamp).all()
    payer_balances = {}
    spent_points = {}

    # Calculate current available balances for each payer
    for transaction in transactions:
        payer = transaction.payer
        if payer not in payer_balances:
            payer_balances[payer] = 0
        payer_balances[payer] += transaction.points

    # Spend points
    for transaction in transactions:
        if points_to_spend <= 0:
            break

        payer = transaction.payer

        # Skip if payer doesn't have points
        if payer_balances[payer] <= 0:
            continue

        # Determine how much to deduct from this transaction
        effective_points = min(transaction.points, payer_balances[payer])
        deduct = min(effective_points, points_to_spend)

        # Deduct points
        points_to_spend -= deduct
        transaction.points -= deduct
        payer_balances[payer] -= deduct

        # Track deductions for each payer
        if payer not in spent_points:
            spent_points[payer] = 0
        spent_points[payer] -= deduct

        # Update payer's balance
        balance = Balance.query.filter_by(payer=payer).first()
        balance.points -= deduct

    # Format the response
    spent_points_response = [{"payer": payer, "points": spent_points[payer]} for payer in spent_points]

    # Commit changes to the database
    db.session.commit()

    return jsonify(spent_points_response), 200

# Check the balance of each payer in the database
@app.route('/balance', methods=['GET'])
def get_balance():
    balances = Balance.query.all()
    result = {balance.payer: balance.points for balance in balances}
    return jsonify(result), 200

# Run the program on HTTP port 8000
if __name__ == '__main__':
    app.run(port=8000)
