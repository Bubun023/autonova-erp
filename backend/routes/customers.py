from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Customer
from utils import role_required

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')


@customers_bp.route('', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def list_customers():
    """List all customers with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Limit per_page to reasonable value
    per_page = min(per_page, 100)
    
    pagination = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'customers': [customer.to_dict() for customer in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }), 200


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist', 'technician')
def get_customer(customer_id):
    """Get specific customer"""
    include_vehicles = request.args.get('include_vehicles', 'false').lower() == 'true'
    
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    return jsonify({
        'customer': customer.to_dict(include_vehicles=include_vehicles)
    }), 200


@customers_bp.route('', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def create_customer():
    """Create a new customer"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if email is unique (if provided)
    if 'email' in data and data['email']:
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({'error': 'Email already exists'}), 400
    
    # Create customer
    customer = Customer(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data.get('email'),
        phone=data['phone'],
        address=data.get('address'),
        city=data.get('city'),
        state=data.get('state'),
        zip_code=data.get('zip_code')
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({
        'message': 'Customer created successfully',
        'customer': customer.to_dict()
    }), 201


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def update_customer(customer_id):
    """Update a customer"""
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.get_json()
    
    # Check if email is unique (if being updated)
    if 'email' in data and data['email'] and data['email'] != customer.email:
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({'error': 'Email already exists'}), 400
    
    # Update fields
    if 'first_name' in data:
        customer.first_name = data['first_name']
    if 'last_name' in data:
        customer.last_name = data['last_name']
    if 'email' in data:
        customer.email = data['email']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'address' in data:
        customer.address = data['address']
    if 'city' in data:
        customer.city = data['city']
    if 'state' in data:
        customer.state = data['state']
    if 'zip_code' in data:
        customer.zip_code = data['zip_code']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Customer updated successfully',
        'customer': customer.to_dict()
    }), 200


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'manager')
def delete_customer(customer_id):
    """Delete a customer (admin/manager only)"""
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({
        'message': 'Customer deleted successfully'
    }), 200
