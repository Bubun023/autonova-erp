from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User
import re


def get_current_user():
    """Get current authenticated user from JWT token"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def role_required(*allowed_roles):
    """
    Decorator to restrict access based on user roles.
    
    Usage:
        @role_required('admin', 'manager')
        def some_route():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.is_active:
                return jsonify({'error': 'User account is inactive'}), 403
            
            if user.role.name not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': list(allowed_roles),
                    'your_role': user.role.name
                }), 403
            
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_password(password):
    """
    Validate password strength.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    
    if not re.search(r'[A-Za-z]', password):
        return False, 'Password must contain at least one letter'
    
    if not re.search(r'[0-9]', password):
        return False, 'Password must contain at least one number'
    
    return True, None


def validate_email(email):
    """
    Validate email format.
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return True  # Email is optional
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_vin(vin):
    """
    Validate VIN format (17 characters, alphanumeric, excluding I, O, Q).
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not vin:
        return True, None  # VIN is optional
    
    if len(vin) != 17:
        return False, 'VIN must be exactly 17 characters'
    
    # VIN should only contain alphanumeric characters except I, O, Q
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin, re.IGNORECASE):
        return False, 'VIN contains invalid characters (I, O, Q are not allowed)'
    
    return True, None
