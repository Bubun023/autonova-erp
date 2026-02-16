from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Estimate, EstimatePart, EstimateLabour, Customer, Vehicle, InsuranceCompany
from utils import role_required, get_current_user
from datetime import datetime
from decimal import Decimal
import logging

estimates_bp = Blueprint('estimates', __name__, url_prefix='/api/estimates')
logger = logging.getLogger(__name__)


def generate_estimate_number():
    """Generate unique estimate number in format EST-YYYYMMDD-XXXX"""
    today = datetime.utcnow()
    date_part = today.strftime('%Y%m%d')
    prefix = f'EST-{date_part}-'
    
    # Find the highest number for today
    latest = Estimate.query.filter(
        Estimate.estimate_number.like(f'{prefix}%')
    ).order_by(Estimate.estimate_number.desc()).first()
    
    if latest:
        # Extract the sequence number and increment
        try:
            last_num = int(latest.estimate_number.split('-')[-1])
            next_num = last_num + 1
        except (ValueError, IndexError):
            next_num = 1
    else:
        next_num = 1
    
    return f'{prefix}{next_num:04d}'


@estimates_bp.route('', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist', 'technician', 'accountant')
def list_estimates():
    """List all estimates with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to prevent excessive queries
    per_page = min(per_page, 100)
    
    # Filters
    status = request.args.get('status')
    customer_id = request.args.get('customer_id', type=int)
    vehicle_id = request.args.get('vehicle_id', type=int)
    
    query = Estimate.query
    
    if status:
        query = query.filter_by(status=status)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    
    pagination = query.order_by(Estimate.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'estimates': [estimate.to_dict() for estimate in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }), 200


@estimates_bp.route('/<int:estimate_id>', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist', 'technician', 'accountant')
def get_estimate(estimate_id):
    """Get estimate details with parts & labour"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    return jsonify({
        'estimate': estimate.to_dict(include_details=True)
    }), 200


@estimates_bp.route('', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def create_estimate():
    """Create new estimate"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['customer_id', 'vehicle_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Verify customer exists
    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Verify vehicle exists
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    # Verify insurance company if provided
    if data.get('insurance_company_id'):
        insurance_company = InsuranceCompany.query.get(data['insurance_company_id'])
        if not insurance_company:
            return jsonify({'error': 'Insurance company not found'}), 404
    
    # Get current user
    current_user = get_current_user()
    
    # Generate estimate number
    estimate_number = generate_estimate_number()
    
    # Parse estimated completion date if provided
    estimated_completion_date = None
    if data.get('estimated_completion_date'):
        try:
            estimated_completion_date = datetime.fromisoformat(data['estimated_completion_date']).date()
        except ValueError:
            return jsonify({'error': 'Invalid date format for estimated_completion_date'}), 400
    
    # Create new estimate
    estimate = Estimate(
        estimate_number=estimate_number,
        customer_id=data['customer_id'],
        vehicle_id=data['vehicle_id'],
        insurance_company_id=data.get('insurance_company_id'),
        insurance_claim_number=data.get('insurance_claim_number'),
        is_insurance_claim=data.get('is_insurance_claim', False),
        description=data.get('description'),
        estimated_completion_date=estimated_completion_date,
        status='pending',
        created_by=current_user.id
    )
    
    try:
        db.session.add(estimate)
        db.session.commit()
        
        logger.info(f"Estimate created: {estimate.estimate_number} (ID: {estimate.id})")
        
        return jsonify({
            'message': 'Estimate created successfully',
            'estimate': estimate.to_dict(include_details=True)
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating estimate: {str(e)}")
        return jsonify({'error': 'Failed to create estimate'}), 500


@estimates_bp.route('/<int:estimate_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def update_estimate(estimate_id):
    """Update estimate (only if status is 'pending')"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only edit pending estimates'}), 400
    
    data = request.get_json()
    
    # Verify customer if being changed
    if 'customer_id' in data:
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        estimate.customer_id = data['customer_id']
    
    # Verify vehicle if being changed
    if 'vehicle_id' in data:
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        estimate.vehicle_id = data['vehicle_id']
    
    # Verify insurance company if being changed
    if 'insurance_company_id' in data:
        if data['insurance_company_id']:
            insurance_company = InsuranceCompany.query.get(data['insurance_company_id'])
            if not insurance_company:
                return jsonify({'error': 'Insurance company not found'}), 404
        estimate.insurance_company_id = data['insurance_company_id']
    
    # Update fields if provided
    if 'insurance_claim_number' in data:
        estimate.insurance_claim_number = data['insurance_claim_number']
    if 'is_insurance_claim' in data:
        estimate.is_insurance_claim = data['is_insurance_claim']
    if 'description' in data:
        estimate.description = data['description']
    if 'estimated_completion_date' in data:
        if data['estimated_completion_date']:
            try:
                estimate.estimated_completion_date = datetime.fromisoformat(data['estimated_completion_date']).date()
            except ValueError:
                return jsonify({'error': 'Invalid date format for estimated_completion_date'}), 400
        else:
            estimate.estimated_completion_date = None
    
    try:
        db.session.commit()
        
        logger.info(f"Estimate updated: ID {estimate_id}")
        
        return jsonify({
            'message': 'Estimate updated successfully',
            'estimate': estimate.to_dict(include_details=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating estimate {estimate_id}: {str(e)}")
        return jsonify({'error': 'Failed to update estimate'}), 500


@estimates_bp.route('/<int:estimate_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'manager')
def delete_estimate(estimate_id):
    """Delete estimate (admin/manager only, only if pending)"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only delete pending estimates'}), 400
    
    try:
        db.session.delete(estimate)
        db.session.commit()
        
        logger.info(f"Estimate deleted: ID {estimate_id}")
        
        return jsonify({
            'message': 'Estimate deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting estimate {estimate_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete estimate'}), 500


@estimates_bp.route('/<int:estimate_id>/approve', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager')
def approve_estimate(estimate_id):
    """Approve estimate (manager/admin only)"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only approve pending estimates'}), 400
    
    # Get current user
    current_user = get_current_user()
    
    # Update estimate status
    estimate.status = 'approved'
    estimate.approved_by = current_user.id
    estimate.approved_at = datetime.utcnow()
    estimate.rejection_reason = None
    
    try:
        db.session.commit()
        
        logger.info(f"Estimate approved: ID {estimate_id} by user {current_user.id}")
        
        return jsonify({
            'message': 'Estimate approved successfully',
            'estimate': estimate.to_dict(include_details=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error approving estimate {estimate_id}: {str(e)}")
        return jsonify({'error': 'Failed to approve estimate'}), 500


@estimates_bp.route('/<int:estimate_id>/reject', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager')
def reject_estimate(estimate_id):
    """Reject estimate (manager/admin only)"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only reject pending estimates'}), 400
    
    data = request.get_json()
    
    # Get rejection reason
    rejection_reason = data.get('rejection_reason')
    
    # Get current user
    current_user = get_current_user()
    
    # Update estimate status
    estimate.status = 'rejected'
    estimate.approved_by = current_user.id
    estimate.approved_at = datetime.utcnow()
    estimate.rejection_reason = rejection_reason
    
    try:
        db.session.commit()
        
        logger.info(f"Estimate rejected: ID {estimate_id} by user {current_user.id}")
        
        return jsonify({
            'message': 'Estimate rejected successfully',
            'estimate': estimate.to_dict(include_details=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting estimate {estimate_id}: {str(e)}")
        return jsonify({'error': 'Failed to reject estimate'}), 500


# Estimate Parts endpoints

@estimates_bp.route('/<int:estimate_id>/parts', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def add_parts_to_estimate(estimate_id):
    """Add parts to estimate"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only add parts to pending estimates'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['part_name', 'quantity', 'unit_price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate quantity and unit_price
    quantity = data['quantity']
    unit_price = data['unit_price']
    
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than 0'}), 400
    
    # Allow zero unit price for free parts (warranty, promotional items, etc.)
    if unit_price < 0:
        return jsonify({'error': 'Unit price cannot be negative'}), 400
    
    # Calculate total price
    unit_price_decimal = Decimal(str(unit_price))
    total_price = Decimal(str(quantity)) * unit_price_decimal
    
    # Create new part
    part = EstimatePart(
        estimate_id=estimate_id,
        part_name=data['part_name'],
        part_number=data.get('part_number'),
        quantity=quantity,
        unit_price=unit_price_decimal,
        total_price=total_price,
        notes=data.get('notes')
    )
    
    try:
        db.session.add(part)
        
        # Recalculate estimate totals
        estimate.calculate_totals()
        
        db.session.commit()
        
        logger.info(f"Part added to estimate {estimate_id}: {part.part_name} (ID: {part.id})")
        
        return jsonify({
            'message': 'Part added successfully',
            'part': part.to_dict(),
            'estimate': estimate.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding part to estimate {estimate_id}: {str(e)}")
        return jsonify({'error': 'Failed to add part'}), 500


@estimates_bp.route('/<int:estimate_id>/parts/<int:part_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def update_estimate_part(estimate_id, part_id):
    """Update estimate part"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only update parts of pending estimates'}), 400
    
    part = EstimatePart.query.get(part_id)
    if not part:
        return jsonify({'error': 'Part not found'}), 404
    
    # Verify part belongs to estimate
    if part.estimate_id != estimate_id:
        return jsonify({'error': 'Part does not belong to this estimate'}), 400
    
    data = request.get_json()
    
    # Update fields if provided
    if 'part_name' in data:
        part.part_name = data['part_name']
    if 'part_number' in data:
        part.part_number = data['part_number']
    if 'quantity' in data:
        if data['quantity'] <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400
        part.quantity = data['quantity']
    if 'unit_price' in data:
        # Allow zero unit price for free parts (warranty, promotional items, etc.)
        if data['unit_price'] < 0:
            return jsonify({'error': 'Unit price cannot be negative'}), 400
        part.unit_price = Decimal(str(data['unit_price']))
    if 'notes' in data:
        part.notes = data['notes']
    
    # Recalculate total price
    part.total_price = Decimal(str(part.quantity)) * part.unit_price
    
    try:
        # Recalculate estimate totals
        estimate.calculate_totals()
        
        db.session.commit()
        
        logger.info(f"Part updated: ID {part_id}")
        
        return jsonify({
            'message': 'Part updated successfully',
            'part': part.to_dict(),
            'estimate': estimate.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating part {part_id}: {str(e)}")
        return jsonify({'error': 'Failed to update part'}), 500


@estimates_bp.route('/<int:estimate_id>/parts/<int:part_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def delete_estimate_part(estimate_id, part_id):
    """Remove part from estimate"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only remove parts from pending estimates'}), 400
    
    part = EstimatePart.query.get(part_id)
    if not part:
        return jsonify({'error': 'Part not found'}), 404
    
    # Verify part belongs to estimate
    if part.estimate_id != estimate_id:
        return jsonify({'error': 'Part does not belong to this estimate'}), 400
    
    try:
        db.session.delete(part)
        
        # Recalculate estimate totals
        estimate.calculate_totals()
        
        db.session.commit()
        
        logger.info(f"Part deleted: ID {part_id}")
        
        return jsonify({
            'message': 'Part removed successfully',
            'estimate': estimate.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting part {part_id}: {str(e)}")
        return jsonify({'error': 'Failed to remove part'}), 500


# Estimate Labour endpoints

@estimates_bp.route('/<int:estimate_id>/labour', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def add_labour_to_estimate(estimate_id):
    """Add labour item to estimate"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only add labour to pending estimates'}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['description', 'hours', 'hourly_rate']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate hours and hourly_rate
    hours = data['hours']
    hourly_rate = data['hourly_rate']
    
    if hours <= 0:
        return jsonify({'error': 'Hours must be greater than 0'}), 400
    
    # Labour cannot be free - hourly rate must be positive
    if hourly_rate <= 0:
        return jsonify({'error': 'Hourly rate must be greater than 0'}), 400
    
    # Calculate total cost
    hours_decimal = Decimal(str(hours))
    hourly_rate_decimal = Decimal(str(hourly_rate))
    total_cost = hours_decimal * hourly_rate_decimal
    
    # Create new labour item
    labour = EstimateLabour(
        estimate_id=estimate_id,
        description=data['description'],
        hours=hours_decimal,
        hourly_rate=hourly_rate_decimal,
        total_cost=total_cost,
        notes=data.get('notes')
    )
    
    try:
        db.session.add(labour)
        
        # Recalculate estimate totals
        estimate.calculate_totals()
        
        db.session.commit()
        
        logger.info(f"Labour added to estimate {estimate_id}: {labour.description} (ID: {labour.id})")
        
        return jsonify({
            'message': 'Labour added successfully',
            'labour': labour.to_dict(),
            'estimate': estimate.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding labour to estimate {estimate_id}: {str(e)}")
        return jsonify({'error': 'Failed to add labour'}), 500


@estimates_bp.route('/<int:estimate_id>/labour/<int:labour_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def update_estimate_labour(estimate_id, labour_id):
    """Update estimate labour item"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only update labour of pending estimates'}), 400
    
    labour = EstimateLabour.query.get(labour_id)
    if not labour:
        return jsonify({'error': 'Labour not found'}), 404
    
    # Verify labour belongs to estimate
    if labour.estimate_id != estimate_id:
        return jsonify({'error': 'Labour does not belong to this estimate'}), 400
    
    data = request.get_json()
    
    # Update fields if provided
    if 'description' in data:
        labour.description = data['description']
    if 'hours' in data:
        if data['hours'] <= 0:
            return jsonify({'error': 'Hours must be greater than 0'}), 400
        labour.hours = Decimal(str(data['hours']))
    if 'hourly_rate' in data:
        # Labour cannot be free - hourly rate must be positive
        if data['hourly_rate'] <= 0:
            return jsonify({'error': 'Hourly rate must be greater than 0'}), 400
        labour.hourly_rate = Decimal(str(data['hourly_rate']))
    if 'notes' in data:
        labour.notes = data['notes']
    
    # Recalculate total cost
    labour.total_cost = labour.hours * labour.hourly_rate
    
    try:
        # Recalculate estimate totals
        estimate.calculate_totals()
        
        db.session.commit()
        
        logger.info(f"Labour updated: ID {labour_id}")
        
        return jsonify({
            'message': 'Labour updated successfully',
            'labour': labour.to_dict(),
            'estimate': estimate.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating labour {labour_id}: {str(e)}")
        return jsonify({'error': 'Failed to update labour'}), 500


@estimates_bp.route('/<int:estimate_id>/labour/<int:labour_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist')
def delete_estimate_labour(estimate_id, labour_id):
    """Remove labour item from estimate"""
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        return jsonify({'error': 'Estimate not found'}), 404
    
    # Check if estimate is pending
    if estimate.status != 'pending':
        return jsonify({'error': 'Can only remove labour from pending estimates'}), 400
    
    labour = EstimateLabour.query.get(labour_id)
    if not labour:
        return jsonify({'error': 'Labour not found'}), 404
    
    # Verify labour belongs to estimate
    if labour.estimate_id != estimate_id:
        return jsonify({'error': 'Labour does not belong to this estimate'}), 400
    
    try:
        db.session.delete(labour)
        
        # Recalculate estimate totals
        estimate.calculate_totals()
        
        db.session.commit()
        
        logger.info(f"Labour deleted: ID {labour_id}")
        
        return jsonify({
            'message': 'Labour removed successfully',
            'estimate': estimate.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting labour {labour_id}: {str(e)}")
        return jsonify({'error': 'Failed to remove labour'}), 500
