from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User


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
