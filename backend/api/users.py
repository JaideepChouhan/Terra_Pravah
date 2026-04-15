"""
Terra Pravah - Users API
========================
User profile and settings management.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models.models import db, User, Notification, AuditLog, APIKey
import secrets
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict(include_private=True)
    })


@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    updatable_fields = [
        'first_name', 'last_name', 'company', 'job_title',
        'phone', 'timezone', 'language'
    ]
    
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict(include_private=True)
    })


@users_bp.route('/me/password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new passwords are required'}), 400
    
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    # Log action
    log = AuditLog(
        user_id=user_id,
        action='password_change',
        resource_type='user',
        resource_id=user_id,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': 'Password changed successfully'
    })


@users_bp.route('/me/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """Get user preferences."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Default preferences
    default_prefs = {
        'theme': 'dark',
        'units': 'metric',
        'notifications': {
            'email_analysis_complete': True,
            'email_project_shared': True,
            'email_comment_mention': True,
            'push_enabled': True
        },
        'workspace': {
            'show_grid': True,
            'show_coordinates': True,
            'default_view': '3d'
        }
    }
    
    # Merge with user preferences
    prefs = {**default_prefs, **(user.preferences or {})}
    
    return jsonify({
        'preferences': prefs
    })


@users_bp.route('/me/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """Update user preferences."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Merge with existing preferences
    if user.preferences:
        user.preferences = {**user.preferences, **data}
    else:
        user.preferences = data
    
    db.session.commit()
    
    return jsonify({
        'message': 'Preferences updated successfully',
        'preferences': user.preferences
    })


@users_bp.route('/me/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications."""
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = Notification.query.filter_by(user_id=user_id)
    
    if unread_only:
        query = query.filter_by(read=False)
    
    query = query.order_by(Notification.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Count unread
    unread_count = Notification.query.filter_by(
        user_id=user_id,
        read=False
    ).count()
    
    return jsonify({
        'notifications': [n.to_dict() for n in pagination.items],
        'total': pagination.total,
        'unread_count': unread_count,
        'pages': pagination.pages,
        'current_page': page
    })


@users_bp.route('/me/notifications/<notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read."""
    user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=user_id
    ).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Notification marked as read'
    })


@users_bp.route('/me/notifications/read-all', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read."""
    user_id = get_jwt_identity()
    
    Notification.query.filter_by(
        user_id=user_id,
        read=False
    ).update({
        'read': True,
        'read_at': datetime.utcnow()
    })
    
    db.session.commit()
    
    return jsonify({
        'message': 'All notifications marked as read'
    })


@users_bp.route('/me/api-keys', methods=['GET'])
@jwt_required()
def list_api_keys():
    """List user's API keys."""
    user_id = get_jwt_identity()
    
    keys = APIKey.query.filter_by(
        user_id=user_id,
        active=True
    ).all()
    
    return jsonify({
        'api_keys': [{
            'id': k.id,
            'name': k.name,
            'prefix': k.prefix,
            'scopes': k.scopes,
            'last_used_at': k.last_used_at.isoformat() if k.last_used_at else None,
            'created_at': k.created_at.isoformat() if k.created_at else None
        } for k in keys]
    })


@users_bp.route('/me/api-keys', methods=['POST'])
@jwt_required()
def create_api_key():
    """Create a new API key."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    name = data.get('name', '').strip()
    scopes = data.get('scopes', ['read'])
    
    if not name:
        return jsonify({'error': 'API key name is required'}), 400
    
    # Generate key
    raw_key = secrets.token_urlsafe(32)
    prefix = raw_key[:8]
    key_hash = generate_password_hash(raw_key)
    
    api_key = APIKey(
        user_id=user_id,
        name=name,
        key_hash=key_hash,
        prefix=prefix,
        scopes=scopes
    )
    
    db.session.add(api_key)
    db.session.commit()
    
    # Return the raw key only once
    return jsonify({
        'message': 'API key created successfully',
        'api_key': {
            'id': api_key.id,
            'name': api_key.name,
            'key': f'tp_{raw_key}',  # Full key with prefix
            'scopes': api_key.scopes
        },
        'warning': 'This is the only time the full key will be shown. Please save it securely.'
    }), 201


@users_bp.route('/me/api-keys/<key_id>', methods=['DELETE'])
@jwt_required()
def revoke_api_key(key_id):
    """Revoke an API key."""
    user_id = get_jwt_identity()
    
    api_key = APIKey.query.filter_by(
        id=key_id,
        user_id=user_id
    ).first()
    
    if not api_key:
        return jsonify({'error': 'API key not found'}), 404
    
    api_key.active = False
    db.session.commit()
    
    return jsonify({
        'message': 'API key revoked successfully'
    })


@users_bp.route('/me/usage', methods=['GET'])
@jwt_required()
def get_usage():
    """Get user usage statistics."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    plan = current_app.config['PLANS'].get(user.subscription_plan, {})
    
    return jsonify({
        'usage': {
            'storage': {
                'used_bytes': user.storage_used_bytes,
                'used_mb': user.storage_used_bytes / (1024 * 1024),
                'limit_mb': plan.get('max_file_size_mb', 100),
                'percentage': (user.storage_used_bytes / (plan.get('max_file_size_mb', 100) * 1024 * 1024)) * 100
            },
            'projects': {
                'count': user.projects_count,
                'limit': plan.get('max_projects', 3),
                'percentage': (user.projects_count / plan.get('max_projects', 3)) * 100 if plan.get('max_projects', 3) > 0 else 0
            },
            'api_calls': {
                'this_month': user.api_calls_this_month,
                'limit': 10000 if 'api_access' in plan.get('features', []) else 0
            }
        },
        'plan': {
            'name': plan.get('name', user.subscription_plan),
            'features': plan.get('features', [])
        }
    })


@users_bp.route('/me/activity', methods=['GET'])
@jwt_required()
def get_activity():
    """Get user activity log."""
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = AuditLog.query.filter_by(user_id=user_id)
    query = query.order_by(AuditLog.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'activity': [{
            'action': log.action,
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'details': log.details,
            'created_at': log.created_at.isoformat() if log.created_at else None
        } for log in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })
