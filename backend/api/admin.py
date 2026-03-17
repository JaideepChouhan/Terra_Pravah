"""
Terra Pravah - Admin API
========================
Administration panel endpoints.
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from backend.models.models import db, User, Project, Team, AnalysisJob, AuditLog

admin_bp = Blueprint('admin', __name__)


def require_admin(f):
    """Decorator to require admin privileges."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        admin_emails = {
            email.strip().lower()
            for email in current_app.config.get('ADMIN_EMAILS', '').split(',')
            if email.strip()
        }

        if not user or (admin_emails and user.email.lower() not in admin_emails):
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_admin
def admin_dashboard():
    """Get admin dashboard statistics."""
    
    # User statistics
    total_users = User.query.count()
    new_users_30d = User.query.filter(
        User.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    active_users_7d = User.query.filter(
        User.last_login_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Project statistics
    total_projects = Project.query.count()
    completed_projects = Project.query.filter_by(status='completed').count()
    
    # Analysis jobs
    total_jobs = AnalysisJob.query.count()
    completed_jobs = AnalysisJob.query.filter_by(status='completed').count()
    failed_jobs = AnalysisJob.query.filter_by(status='failed').count()
    
    # Storage usage
    total_storage = db.session.query(func.sum(User.storage_used_bytes)).scalar() or 0
    
    return jsonify({
        'users': {
            'total': total_users,
            'new_30d': new_users_30d,
            'active_7d': active_users_7d
        },
        'projects': {
            'total': total_projects,
            'completed': completed_projects,
            'completion_rate': (completed_projects / total_projects * 100) if total_projects > 0 else 0
        },
        'analysis': {
            'total_jobs': total_jobs,
            'completed': completed_jobs,
            'failed': failed_jobs,
            'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        },
        'storage': {
            'total_bytes': total_storage,
            'total_gb': total_storage / (1024 ** 3)
        }
    })


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@require_admin
def list_all_users():
    """List all users with filtering and pagination."""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    query = User.query
    
    if search:
        query = query.filter(
            User.email.ilike(f'%{search}%') |
            User.first_name.ilike(f'%{search}%') |
            User.last_name.ilike(f'%{search}%')
        )
    
    # Sort
    sort_column = getattr(User, sort_by, User.created_at)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [u.to_dict(include_private=True) for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@admin_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
@require_admin
def get_user_details(user_id):
    """Get detailed user information."""
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's projects
    projects = Project.query.filter_by(owner_id=user_id).all()
    
    # Get recent activity
    recent_activity = AuditLog.query.filter_by(user_id=user_id).order_by(
        AuditLog.created_at.desc()
    ).limit(20).all()
    
    return jsonify({
        'user': user.to_dict(include_private=True),
        'projects': [p.to_dict() for p in projects],
        'activity': [{
            'action': log.action,
            'resource_type': log.resource_type,
            'created_at': log.created_at.isoformat()
        } for log in recent_activity]
    })


@admin_bp.route('/projects', methods=['GET'])
@jwt_required()
@require_admin
def list_all_projects():
    """List all projects with filtering."""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    status = request.args.get('status')
    
    query = Project.query
    
    if status:
        query = query.filter(Project.status == status)
    
    query = query.order_by(Project.updated_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'projects': [p.to_dict(include_details=True) for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@require_admin
def list_audit_logs():
    """List audit logs for compliance."""
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    action = request.args.get('action')
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = AuditLog.query
    
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if start_date:
        query = query.filter(AuditLog.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(AuditLog.created_at <= datetime.fromisoformat(end_date))
    
    query = query.order_by(AuditLog.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'logs': [{
            'id': log.id,
            'user_id': log.user_id,
            'action': log.action,
            'resource_type': log.resource_type,
            'resource_id': log.resource_id,
            'ip_address': log.ip_address,
            'details': log.details,
            'created_at': log.created_at.isoformat()
        } for log in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@admin_bp.route('/system/health', methods=['GET'])
@jwt_required()
@require_admin
def system_health():
    """Get system health status."""
    
    # Database check
    try:
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # Check storage
    import shutil
    upload_path = current_app.config['UPLOAD_FOLDER']
    total, used, free = shutil.disk_usage(upload_path)
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'components': {
            'database': db_status,
            'storage': {
                'total_gb': total / (1024 ** 3),
                'used_gb': used / (1024 ** 3),
                'free_gb': free / (1024 ** 3),
                'usage_percent': (used / total) * 100
            }
        },
        'version': current_app.config.get('APP_VERSION', '2.0.0')
    })


@admin_bp.route('/analytics/usage', methods=['GET'])
@jwt_required()
@require_admin
def usage_analytics():
    """Get usage analytics over time."""
    
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily signups
    daily_signups = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(
        User.created_at >= start_date
    ).group_by(
        func.date(User.created_at)
    ).all()
    
    # Daily analysis jobs
    daily_jobs = db.session.query(
        func.date(AnalysisJob.created_at),
        func.count(AnalysisJob.id)
    ).filter(
        AnalysisJob.created_at >= start_date
    ).group_by(
        func.date(AnalysisJob.created_at)
    ).all()
    
    return jsonify({
        'period_days': days,
        'signups': {str(date): count for date, count in daily_signups},
        'analysis_jobs': {str(date): count for date, count in daily_jobs}
    })
