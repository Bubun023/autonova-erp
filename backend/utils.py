from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User, db


def get_current_user():
    """Get current authenticated user from JWT token"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)


def role_required(*allowed_roles):
    """
    Decorator to check if user has one of the allowed roles
    Usage: @role_required('admin', 'manager')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user = get_current_user()
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            if not current_user.is_active:
                return jsonify({'error': 'Account is inactive'}), 403
            
            if current_user.role.name not in allowed_roles:
                return jsonify({
                    'error': 'Access denied',
                    'message': f'This action requires one of the following roles: {", ".join(allowed_roles)}'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
