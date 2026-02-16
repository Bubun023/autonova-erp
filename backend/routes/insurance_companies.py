from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, InsuranceCompany
from utils import role_required, validate_email
import logging

insurance_companies_bp = Blueprint('insurance_companies', __name__, url_prefix='/api/insurance-companies')
logger = logging.getLogger(__name__)


@insurance_companies_bp.route('', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist', 'technician', 'accountant')
def list_insurance_companies():
    """List all insurance companies with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to prevent excessive queries
    per_page = min(per_page, 100)
    
    # Filter by active status if provided
    is_active = request.args.get('is_active', type=str)
    
    query = InsuranceCompany.query
    
    if is_active is not None:
        query = query.filter_by(is_active=(is_active.lower() == 'true'))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'insurance_companies': [company.to_dict() for company in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }), 200


@insurance_companies_bp.route('/<int:company_id>', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager', 'receptionist', 'technician', 'accountant')
def get_insurance_company(company_id):
    """Get specific insurance company"""
    company = InsuranceCompany.query.get(company_id)
    if not company:
        return jsonify({'error': 'Insurance company not found'}), 404
    
    return jsonify({
        'insurance_company': company.to_dict()
    }), 200


@insurance_companies_bp.route('', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager')
def create_insurance_company():
    """Create a new insurance company (admin/manager only)"""
    data = request.get_json()
    
    # Validate required fields
    if 'name' not in data:
        return jsonify({'error': 'Missing required field: name'}), 400
    
    # Validate email if provided
    if 'email' in data and data['email'] and not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if company with same name already exists
    existing_company = InsuranceCompany.query.filter_by(name=data['name']).first()
    if existing_company:
        return jsonify({'error': 'Insurance company with this name already exists'}), 400
    
    # Create new insurance company
    company = InsuranceCompany(
        name=data['name'],
        contact_person=data.get('contact_person'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address'),
        is_active=data.get('is_active', True)
    )
    
    try:
        db.session.add(company)
        db.session.commit()
        
        logger.info(f"Insurance company created: {company.name} (ID: {company.id})")
        
        return jsonify({
            'message': 'Insurance company created successfully',
            'insurance_company': company.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating insurance company: {str(e)}")
        return jsonify({'error': 'Failed to create insurance company'}), 500


@insurance_companies_bp.route('/<int:company_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager')
def update_insurance_company(company_id):
    """Update an existing insurance company (admin/manager only)"""
    company = InsuranceCompany.query.get(company_id)
    if not company:
        return jsonify({'error': 'Insurance company not found'}), 404
    
    data = request.get_json()
    
    # Validate email if provided
    if 'email' in data and data['email'] and not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if name is being changed and if it conflicts with another company
    if 'name' in data and data['name'] != company.name:
        existing_company = InsuranceCompany.query.filter_by(name=data['name']).first()
        if existing_company:
            return jsonify({'error': 'Insurance company with this name already exists'}), 400
    
    # Update fields if provided
    if 'name' in data:
        company.name = data['name']
    if 'contact_person' in data:
        company.contact_person = data['contact_person']
    if 'phone' in data:
        company.phone = data['phone']
    if 'email' in data:
        company.email = data['email']
    if 'address' in data:
        company.address = data['address']
    if 'is_active' in data:
        company.is_active = data['is_active']
    
    try:
        db.session.commit()
        
        logger.info(f"Insurance company updated: ID {company_id}")
        
        return jsonify({
            'message': 'Insurance company updated successfully',
            'insurance_company': company.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating insurance company {company_id}: {str(e)}")
        return jsonify({'error': 'Failed to update insurance company'}), 500


@insurance_companies_bp.route('/<int:company_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_insurance_company(company_id):
    """Delete an insurance company (admin only)"""
    company = InsuranceCompany.query.get(company_id)
    if not company:
        return jsonify({'error': 'Insurance company not found'}), 404
    
    try:
        db.session.delete(company)
        db.session.commit()
        
        logger.info(f"Insurance company deleted: ID {company_id}")
        
        return jsonify({
            'message': 'Insurance company deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting insurance company {company_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete insurance company'}), 500
