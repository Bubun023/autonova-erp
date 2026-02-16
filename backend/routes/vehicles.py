from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Vehicle, Customer
from utils import role_required, validate_vin

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/api/vehicles')


@vehicles_bp.route('', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist', 'technician')
def list_vehicles():
    """List all vehicles with pagination and optional customer_id filter"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    customer_id = request.args.get('customer_id', type=int)
    
    # Limit per_page to prevent excessive queries
    per_page = min(per_page, 100)
    
    # Build query
    query = Vehicle.query
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'vehicles': [vehicle.to_dict() for vehicle in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }), 200


@vehicles_bp.route('/<int:vehicle_id>', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist', 'technician')
def get_vehicle(vehicle_id):
    """Get specific vehicle"""
    include_owner = request.args.get('include_owner', 'false').lower() == 'true'
    
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    return jsonify({
        'vehicle': vehicle.to_dict(include_owner=include_owner)
    }), 200


@vehicles_bp.route('', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def create_vehicle():
    """Create a new vehicle"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['customer_id', 'make', 'model', 'year']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate customer exists
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Validate VIN if provided
    if 'vin' in data and data['vin']:
        is_valid, error_message = validate_vin(data['vin'])
        if not is_valid:
            return jsonify({'error': error_message}), 400
    
    # Create new vehicle
    vehicle = Vehicle(
        customer_id=data['customer_id'],
        make=data['make'],
        model=data['model'],
        year=data['year'],
        vin=data.get('vin'),
        license_plate=data.get('license_plate'),
        color=data.get('color'),
        mileage=data.get('mileage')
    )
    
    try:
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle created successfully',
            'vehicle': vehicle.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@vehicles_bp.route('/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist', 'technician')
def update_vehicle(vehicle_id):
    """Update an existing vehicle"""
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'customer_id' in data:
        # Validate customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        vehicle.customer_id = data['customer_id']
    
    if 'vin' in data and data['vin']:
        # Validate VIN
        is_valid, error_message = validate_vin(data['vin'])
        if not is_valid:
            return jsonify({'error': error_message}), 400
        vehicle.vin = data['vin']
    
    if 'make' in data:
        vehicle.make = data['make']
    if 'model' in data:
        vehicle.model = data['model']
    if 'year' in data:
        vehicle.year = data['year']
    if 'license_plate' in data:
        vehicle.license_plate = data['license_plate']
    if 'color' in data:
        vehicle.color = data['color']
    if 'mileage' in data:
        vehicle.mileage = data['mileage']
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@vehicles_bp.route('/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'manager')
def delete_vehicle(vehicle_id):
    """Delete a vehicle (admin/manager only)"""
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    try:
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
