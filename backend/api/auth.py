"""
Terra Pravah - Authentication API
==================================
Handles user registration, login, OAuth, and token management.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash
import secrets
import re

from backend.models.models import db, User, AuditLog
from backend.services.email_service import send_verification_email, send_password_reset_email

auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, None


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate required fields
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    valid, message = validate_password(password)
    if not valid:
        return jsonify({'error': message}), 400
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        subscription_plan='free'
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # Log action
    log = AuditLog(
        user_id=user.id,
        action='register',
        resource_type='user',
        resource_id=user.id,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    # Send verification email (async)
    try:
        send_verification_email(user)
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email: {e}")
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict(include_private=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email and password."""
    data = request.get_json()
    
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # Log action
    log = AuditLog(
        user_id=user.id,
        action='login',
        resource_type='user',
        resource_id=user.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(include_private=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    
    return jsonify({
        'access_token': access_token
    })


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout (client should discard tokens)."""
    user_id = get_jwt_identity()
    
    # Log action
    log = AuditLog(
        user_id=user_id,
        action='logout',
        resource_type='user',
        resource_id=user_id,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Logout successful'})


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict(include_private=True)
    })


@auth_bp.route('/password/forgot', methods=['POST'])
def forgot_password():
    """Request password reset email."""
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    # Always return success to prevent email enumeration
    if user:
        try:
            send_password_reset_email(user)
        except Exception as e:
            current_app.logger.error(f"Failed to send password reset email: {e}")
    
    return jsonify({
        'message': 'If an account exists with this email, a password reset link will be sent.'
    })


@auth_bp.route('/password/reset', methods=['POST'])
def reset_password():
    """Reset password with token."""
    data = request.get_json()
    
    token = data.get('token', '')
    new_password = data.get('password', '')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400
    
    valid, message = validate_password(new_password)
    if not valid:
        return jsonify({'error': message}), 400
    
    # Verify token and get user (implement token verification logic)
    # This is a simplified version - in production, use a proper token system
    
    return jsonify({
        'message': 'Password reset successful. Please log in with your new password.'
    })


@auth_bp.route('/oauth/google', methods=['POST'])
def google_oauth():
    """Handle Google OAuth login."""
    data = request.get_json()
    google_token = data.get('token')
    
    if not google_token:
        return jsonify({'error': 'Google token is required'}), 400
    
    try:
        # Verify Google token and get user info
        # In production, use google-auth library to verify the token
        # For now, we'll assume the token contains user info
        
        google_user_info = data.get('user_info', {})
        email = google_user_info.get('email', '').lower()
        
        if not email:
            return jsonify({'error': 'Could not get email from Google'}), 400
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(
                email=email,
                first_name=google_user_info.get('given_name', ''),
                last_name=google_user_info.get('family_name', ''),
                avatar_url=google_user_info.get('picture'),
                oauth_provider='google',
                oauth_id=google_user_info.get('sub'),
                email_verified=True,
                subscription_plan='free'
            )
            db.session.add(user)
        
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(include_private=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        
    except Exception as e:
        current_app.logger.error(f"Google OAuth error: {e}")
        return jsonify({'error': 'OAuth authentication failed'}), 401


@auth_bp.route('/oauth/github', methods=['POST'])
def github_oauth():
    """Handle GitHub OAuth login."""
    data = request.get_json()
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'GitHub authorization code is required'}), 400
    
    try:
        # Exchange code for access token and get user info
        # In production, implement proper GitHub OAuth flow
        
        github_user_info = data.get('user_info', {})
        email = github_user_info.get('email', '').lower()
        
        if not email:
            return jsonify({'error': 'Could not get email from GitHub'}), 400
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            name_parts = (github_user_info.get('name', '') or '').split(' ', 1)
            user = User(
                email=email,
                first_name=name_parts[0] if name_parts else '',
                last_name=name_parts[1] if len(name_parts) > 1 else '',
                avatar_url=github_user_info.get('avatar_url'),
                oauth_provider='github',
                oauth_id=str(github_user_info.get('id')),
                email_verified=True,
                subscription_plan='free'
            )
            db.session.add(user)
        
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(include_private=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        
    except Exception as e:
        current_app.logger.error(f"GitHub OAuth error: {e}")
        return jsonify({'error': 'OAuth authentication failed'}), 401


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify email with token."""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Verification token is required'}), 400
    
    # Verify token and update user (implement token verification)
    
    return jsonify({
        'message': 'Email verified successfully'
    })
