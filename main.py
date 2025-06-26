import os
import logging
from flask import Flask, render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'fallback-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Routes
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid credentials', logged_in=False)
    return render_template('login.html', logged_in=False)

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', logged_in=True)

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        session.pop('username', None)
        return redirect(url_for('register'))

    return redirect(url_for('dashboard'))

@app.route('/map')
def show_map():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('map.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        category = request.form.get("category")
        result = {}

        if category == "acquisition_cost":
            purchase_price = float(request.form.get("purchase_price") or 0)
            closing_costs = float(request.form.get("closing_costs") or 0)
            renovation_budget = float(request.form.get("renovation_budget") or 0)
            downpayment = float(request.form.get("downpayment") or 0)

            # Validation
            if any(val < 0 for val in [purchase_price, closing_costs, renovation_budget, downpayment]):
                return render_template('dashboard.html', error="Values cannot be negative")

            total_fixed_costs = purchase_price + closing_costs + renovation_budget + downpayment
            result["Total Fixed Costs"] = total_fixed_costs
            
        elif category == "operating_expenses":
            homeowners_insurance = float(request.form.get("homeowners_insurance") or 0)
            property_tax = float(request.form.get("property_tax") or 0)
            other_costs = float(request.form.get("other_cost") or 0)

            # Validation
            if any(val < 0 for val in [homeowners_insurance, property_tax, other_costs]):
                return render_template('dashboard.html', error="Values cannot be negative")

            total_operating_expenses = homeowners_insurance + property_tax + other_costs
            result["Total Operating Expenses"] = total_operating_expenses
            
        elif category == "cash_flow":
            rent_revenue = float(request.form.get("rent_revenue") or 0)
            coc_return_goal = float(request.form.get("coc_return_goal") or 0)
            
            # Validation
            if rent_revenue < 0 or coc_return_goal < 0:
                return render_template('dashboard.html', error="Values cannot be negative")
                
            result["Annual Cash Flow"] = rent_revenue * (coc_return_goal / 100)
            
        elif category == "annual_growth":
            rent_growth = float(request.form.get("rent_growth") or 0)
            appreciation = float(request.form.get("appreciation") or 0)
            other_cost = float(request.form.get("other_cost") or 0)

            result["Annual Growth Total"] = rent_growth + appreciation + other_cost
        else:
            return render_template('dashboard.html', error="Invalid calculation category")

        logging.info(f"Calculation performed for category: {category}")
        return render_template('result.html', result=result)
        
    except (ValueError, TypeError) as e:
        logging.error(f"Calculation error: {str(e)}")
        return render_template('dashboard.html', error="Please enter valid numerical values")

@app.route('/check_credit', methods=['POST'])
def check_credit():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get and validate form data
        credit_score = int(request.form.get('credit_score'))
        salary = float(request.form.get('salary'))
        monthly_debt = float(request.form.get('monthly_debt'))
        loan_amount = float(request.form.get('loan_amount'))

        # Input validation
        if not (300 <= credit_score <= 850):
            return render_template('dashboard.html', error="Credit score must be between 300 and 850")
        if salary < 0 or monthly_debt < 0 or loan_amount < 0:
            return render_template('dashboard.html', error="Values cannot be negative")

        # Calculate Debt-to-Income Ratio (DTI)
        monthly_income = salary / 12
        dti = (monthly_debt / monthly_income) * 100 if monthly_income > 0 else 100

        # Determine loan eligibility and interest rate
        loan_approved = False
        interest_rate = 0.0
        credit_tips = []

        if credit_score >= 740:
            loan_approved = True
            interest_rate = 3.5 if dti < 36 else 4.0
            credit_tips = [
                "Maintain your excellent credit by paying bills on time.",
                "Keep credit utilization below 30%."
            ]
        elif credit_score >= 670:
            loan_approved = True
            interest_rate = 4.5 if dti < 36 else 5.0
            credit_tips = [
                "Continue making timely payments.",
                "Reduce outstanding debt to improve your score."
            ]
        elif credit_score >= 580:
            loan_approved = dti < 43
            interest_rate = 6.5 if dti < 36 else 7.5
            credit_tips = [
                "Pay down existing debt to lower your DTI.",
                "Make all payments on time to build credit history.",
                "Consider a secured credit card to improve your score."
            ]
        else:
            loan_approved = False
            interest_rate = 10.0
            credit_tips = [
                "Work on paying bills on time consistently.",
                "Reduce debt through a payment plan.",
                "Consider credit counseling services."
            ]

        # Calculate maximum affordable loan
        max_loan = (monthly_income * 0.36 - monthly_debt) * 360

        # Calculate monthly payment (assuming 30-year term)
        term_months = 360  # 30 years
        monthly_rate = interest_rate / 100 / 12
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
        else:
            monthly_payment = loan_amount / term_months if loan_amount > 0 else 0

        result = {
            'credit_score': credit_score,
            'loan_approved': loan_approved,
            'interest_rate': interest_rate,
            'dti': round(dti, 2),
            'requested_loan': loan_amount,
            'max_affordable_loan': round(max_loan, 2),
            'monthly_payment': round(monthly_payment, 2) if loan_approved else 0,
            'tips': credit_tips
        }

        return render_template('credit_result.html', result=result)
    except (ValueError, TypeError):
        return render_template('dashboard.html', error="Please enter valid numerical values")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 8080))
    
    app.run(debug=debug_mode, port=port, host='127.0.0.1')