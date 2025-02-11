from flask import Flask , render_template, redirect , request , url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask("__name__")
app.secret_key = 'your_secret_key_here' 

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # no tracking
db = SQLAlchemy(app)


# Database Model
class User(db.Model):
    # Variables 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False) # nullable = not cannot be empty
    password = db.Column(db.String(150), nullable=False)



# Routes
# Login
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template(('login.html'))



# Login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = username # unique session for user
            return redirect(url_for('dashboard'))
        
        # If login fails
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')
#Register
@app.route("/register", methods= ['POST','GET'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # Check if passwords match
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


#Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect if user is not logged in
    return render_template('dashboard.html') 


# Delete User
@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure only logged-in users can delete accounts
    
    user = User.query.filter_by(username=session['username']).first()

    if user:
        db.session.delete(user)
        db.session.commit()
        session.pop('username', None)  # Remove user session after deletion
        return redirect(url_for('register'))  # Redirect to register page after deletion

    return redirect(url_for('dashboard'))  # If user not found, go back to dashboard


# Route to display the interactive map
@app.route('/map')
def show_map():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('map.html')  # Renders the saved map file

@app.route('/calculate', methods=['POST'])
def calculate():
    category = request.form.get("category")
    result = {}

    if category == "acquisition_cost":
        purchase_price = float(request.form.get("purchase_price", 0))
        closing_costs = float(request.form.get("closing_costs", 0))
        renovation_budget = float(request.form.get("renovation_budget", 0))
        downpayment = float(request.form.get("downpayment", 0))

        total_fixed_costs = purchase_price + closing_costs + renovation_budget + downpayment
        result["Total Fixed Costs"] = total_fixed_costs

    elif category == "operating_expenses":
        homeowners_insurance = float(request.form.get("homeowners_insurance", 0))
        property_tax = float(request.form.get("property_tax", 0))
        other_costs = float(request.form.get("other_cost", 0))

        total_operating_expenses = homeowners_insurance + property_tax + other_costs
        result["Total Operating Expenses"] = total_operating_expenses

    elif category == "cash_flow":
        rent_revenue = float(request.form.get("rent_revenue", 0))
        coc_return_goal = float(request.form.get("coc_return_goal", 0))

        result["Annual Cash Flow"] = rent_revenue * (coc_return_goal / 100)

    elif category == "annual_growth":
        rent_growth = float(request.form.get("rent_growth", 0))
        appreciation = float(request.form.get("appreciation", 0))
        other_cost = float(request.form.get("other_cost", 0))

        result["Annual Growth Total"] = rent_growth + appreciation + other_cost

    return render_template('result.html', result=result)



if __name__  in "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)