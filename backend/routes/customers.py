from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Customer
from utils import role_required, validate_email
import logging

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')
logger = logging.getLogger(__name__)


@customers_bp.route('', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def list_customers():
    """List all customers with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to prevent excessive queries
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
    
    # Validate email if provided
    if 'email' in data and data['email'] and not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Create new customer
    customer = Customer(
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data['phone'],
        email=data.get('email'),
        address=data.get('address')
    )
    
    try:
        db.session.add(customer)
        db.session.commit()
        
        logger.info(f"Customer created: {customer.first_name} {customer.last_name} (ID: {customer.id})")
        
        return jsonify({
            'message': 'Customer created successfully',
            'customer': customer.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating customer: {str(e)}")
        return jsonify({'error': 'Failed to create customer'}), 500


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def update_customer(customer_id):
    """Update an existing customer"""
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.get_json()
    
    # Validate email if provided
    if 'email' in data and data['email'] and not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Update fields if provided
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
    
    try:
        db.session.commit()
        
        logger.info(f"Customer updated: ID {customer_id}")
        
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating customer {customer_id}: {str(e)}")
        return jsonify({'error': 'Failed to update customer'}), 500


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'manager')
def delete_customer(customer_id):
    """Delete a customer (admin/manager only)"""
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    try:
        db.session.delete(customer)
        db.session.commit()
        
        logger.info(f"Customer deleted: ID {customer_id}")
        
        return jsonify({
            'message': 'Customer deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting customer {customer_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete customer'}), 500
