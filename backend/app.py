from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

from config import Config
from models import db, User, Customer, Vehicle, Role, Technician, Supplier, InsuranceCompany

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Home route
@app.route('/')
def home():
    return "Welcome to AutoNova ERP!"

# Register route
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_pw,
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        role_id=data['role_id']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"})

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        token = create_access_token(identity=user.id)
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

# Customers routes
@app.route('/customers', methods=['POST'])
@jwt_required()
def add_customer():
    data = request.json
    new_customer = Customer(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data['phone'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code']
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "Customer added"}), 201

@app.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    customers = Customer.query.all()
    result = []
    for c in customers:
        result.append({
            "id": c.id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "phone": c.phone,
            "address": c.address,
            "city": c.city,
            "state": c.state,
            "zip_code": c.zip_code
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
    
