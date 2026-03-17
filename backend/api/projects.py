"""
Terra Pravah - Projects API
============================
CRUD operations for drainage design projects.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from pathlib import Path
import shutil

from backend.models.models import (
    db, Project, ProjectVersion, User, Team, 
    AnalysisJob, Comment, AuditLog
)

projects_bp = Blueprint('projects', __name__)


def check_project_access(project, user_id, required_permission='viewer'):
    """Check if user has access to project."""
    permission_levels = ['viewer', 'commenter', 'editor', 'owner']
    required_level = permission_levels.index(required_permission)
    
    # Owner always has full access
    if project.owner_id == user_id:
        return True
    
    # Check collaborator permissions
    for collab in project.collaborators:
        if collab.id == user_id:
            # Get permission from association table
            return True  # Simplified - check actual permission in production
    
    # Check team membership
    if project.team:
        user = User.query.get(user_id)
        if user and project.team in user.teams:
            return True
    
    # Public projects are viewable by all
    if project.visibility == 'public' and required_permission == 'viewer':
        return True
    
    return False


@projects_bp.route('', methods=['GET'])
@jwt_required()
def list_projects():
    """List all projects accessible to user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'updated_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Base query - owned projects
    query = Project.query.filter(
        (Project.owner_id == user_id) |
        (Project.visibility == 'public')
    )
    
    # Filter by status
    if status:
        query = query.filter(Project.status == status)
    
    # Search
    if search:
        query = query.filter(
            Project.name.ilike(f'%{search}%') |
            Project.description.ilike(f'%{search}%') |
            Project.location_name.ilike(f'%{search}%')
        )
    
    # Sort
    sort_column = getattr(Project, sort_by, Project.updated_at)
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'projects': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Project name is required'}), 400
    
    # Create project
    project = Project(
        name=name,
        description=data.get('description', ''),
        location_name=data.get('location_name'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        epsg_code=data.get('epsg_code'),
        units=data.get('units', 'metric'),
        design_storm_years=data.get('design_storm_years', 10),
        runoff_coefficient=data.get('runoff_coefficient', 0.5),
        flow_algorithm=data.get('flow_algorithm', 'dinf'),
        visibility=data.get('visibility', 'private'),
        tags=data.get('tags', []),
        owner_id=user_id,
        team_id=data.get('team_id')
    )
    
    db.session.add(project)
    
    # Update user project count
    user.projects_count += 1
    
    # Log action
    log = AuditLog(
        user_id=user_id,
        action='create',
        resource_type='project',
        resource_id=project.id,
        ip_address=request.remote_addr,
        details={'name': name}
    )
    db.session.add(log)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Project created successfully',
        'project': project.to_dict(include_details=True)
    }), 201


@projects_bp.route('/<project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get project details."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_project_access(project, user_id, 'viewer'):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'project': project.to_dict(include_details=True)
    })


@projects_bp.route('/<project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update project details."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_project_access(project, user_id, 'editor'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Track changes for audit
    changes = {}
    
    # Update allowed fields
    updatable_fields = [
        'name', 'description', 'location_name', 'latitude', 'longitude',
        'epsg_code', 'units', 'design_storm_years', 'runoff_coefficient',
        'flow_algorithm', 'visibility', 'tags'
    ]
    
    for field in updatable_fields:
        if field in data:
            old_value = getattr(project, field)
            new_value = data[field]
            if old_value != new_value:
                changes[field] = {'old': old_value, 'new': new_value}
                setattr(project, field, new_value)
    
    # Log changes
    if changes:
        log = AuditLog(
            user_id=user_id,
            action='update',
            resource_type='project',
            resource_id=project_id,
            ip_address=request.remote_addr,
            changes=changes
        )
        db.session.add(log)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Project updated successfully',
        'project': project.to_dict(include_details=True)
    })


@projects_bp.route('/<project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete a project."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Only the owner can delete a project'}), 403
    
    # Delete associated files
    try:
        if project.results_path:
            results_path = Path(project.results_path)
            if results_path.exists():
                shutil.rmtree(results_path)
        
        if project.dtm_file_path:
            dtm_path = Path(project.dtm_file_path)
            if dtm_path.exists():
                dtm_path.unlink()
    except Exception as e:
        current_app.logger.error(f"Error deleting project files: {e}")
    
    # Update user project count
    user = User.query.get(user_id)
    if user and user.projects_count > 0:
        user.projects_count -= 1
    
    # Log action
    log = AuditLog(
        user_id=user_id,
        action='delete',
        resource_type='project',
        resource_id=project_id,
        ip_address=request.remote_addr,
        details={'name': project.name}
    )
    db.session.add(log)
    
    # Delete project
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({
        'message': 'Project deleted successfully'
    })


@projects_bp.route('/<project_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_project(project_id):
    """Duplicate a project."""
    user_id = get_jwt_identity()
    original = Project.query.get(project_id)
    
    if not original:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_project_access(original, user_id, 'viewer'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json() or {}
    
    # Create duplicate
    duplicate = Project(
        name=data.get('name', f"{original.name} (Copy)"),
        description=original.description,
        location_name=original.location_name,
        latitude=original.latitude,
        longitude=original.longitude,
        epsg_code=original.epsg_code,
        units=original.units,
        design_storm_years=original.design_storm_years,
        runoff_coefficient=original.runoff_coefficient,
        flow_algorithm=original.flow_algorithm,
        visibility='private',
        tags=original.tags.copy() if original.tags else [],
        owner_id=user_id
    )
    
    db.session.add(duplicate)
    db.session.commit()
    
    return jsonify({
        'message': 'Project duplicated successfully',
        'project': duplicate.to_dict(include_details=True)
    }), 201


@projects_bp.route('/<project_id>/share', methods=['POST'])
@jwt_required()
def share_project(project_id):
    """Share project with another user."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if project.owner_id != user_id:
        return jsonify({'error': 'Only the owner can share the project'}), 403
    
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    permission = data.get('permission', 'viewer')
    
    if permission not in ['viewer', 'commenter', 'editor']:
        return jsonify({'error': 'Invalid permission level'}), 400
    
    # Find user by email
    target_user = User.query.filter_by(email=email).first()
    
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    if target_user.id == user_id:
        return jsonify({'error': 'Cannot share with yourself'}), 400
    
    # Add collaborator
    if target_user not in project.collaborators:
        project.collaborators.append(target_user)
        db.session.commit()
    
    return jsonify({
        'message': f'Project shared with {email}',
        'collaborator': target_user.to_dict()
    })


@projects_bp.route('/<project_id>/collaborators', methods=['GET'])
@jwt_required()
def list_collaborators(project_id):
    """List project collaborators."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_project_access(project, user_id, 'viewer'):
        return jsonify({'error': 'Access denied'}), 403
    
    collaborators = [{
        'user': c.to_dict(),
        'permission': 'collaborator'  # Get actual permission in production
    } for c in project.collaborators]
    
    # Add owner
    collaborators.insert(0, {
        'user': project.owner.to_dict(),
        'permission': 'owner'
    })
    
    return jsonify({
        'collaborators': collaborators
    })


@projects_bp.route('/<project_id>/versions', methods=['GET'])
@jwt_required()
def list_versions(project_id):
    """List project versions."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_project_access(project, user_id, 'viewer'):
        return jsonify({'error': 'Access denied'}), 403
    
    versions = project.versions.all()
    
    return jsonify({
        'versions': [v.to_dict() for v in versions]
    })


@projects_bp.route('/<project_id>/versions', methods=['POST'])
@jwt_required()
def create_version(project_id):
    """Create a new version snapshot."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_project_access(project, user_id, 'editor'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json() or {}
    
    # Get latest version number
    latest_version = project.versions.first()
    new_version_num = (latest_version.version + 1) if latest_version else 1
    
    version = ProjectVersion(
        project_id=project_id,
        version=new_version_num,
        name=data.get('name', f'Version {new_version_num}'),
        description=data.get('description'),
        config_snapshot={
            'design_storm_years': project.design_storm_years,
            'runoff_coefficient': project.runoff_coefficient,
            'flow_algorithm': project.flow_algorithm
        },
        results_snapshot={
            'total_channels': project.total_channels,
            'total_length_km': project.total_length_km,
            'total_outlets': project.total_outlets,
            'peak_flow_m3s': project.peak_flow_m3s
        },
        created_by_id=user_id
    )
    
    db.session.add(version)
    db.session.commit()
    
    return jsonify({
        'message': 'Version created successfully',
        'version': version.to_dict()
    }), 201


@projects_bp.route('/<project_id>/comments', methods=['GET'])
@jwt_required()
def list_comments(project_id):
    """List project comments."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_project_access(project, user_id, 'viewer'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Get top-level comments only
    comments = Comment.query.filter_by(
        project_id=project_id,
        parent_id=None
    ).order_by(Comment.created_at.desc()).all()
    
    return jsonify({
        'comments': [c.to_dict() for c in comments]
    })


@projects_bp.route('/<project_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(project_id):
    """Create a comment on a project."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_project_access(project, user_id, 'commenter'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Comment content is required'}), 400
    
    comment = Comment(
        project_id=project_id,
        user_id=user_id,
        content=content,
        location_x=data.get('location_x'),
        location_y=data.get('location_y'),
        element_id=data.get('element_id'),
        parent_id=data.get('parent_id')
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'message': 'Comment added successfully',
        'comment': comment.to_dict()
    }), 201


@projects_bp.route('/<project_id>/export/<format>', methods=['GET'])
@jwt_required()
def export_project(project_id, format):
    """Export project data in various formats."""
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_project_access(project, user_id, 'viewer'):
        return jsonify({'error': 'Access denied'}), 403
    
    if format not in ['geojson', 'shapefile', 'kml', 'dxf', 'csv', 'pdf']:
        return jsonify({'error': 'Unsupported export format'}), 400
    
    if format == 'geojson' and project.geojson_path:
        geojson_path = Path(project.geojson_path)
        if geojson_path.exists():
            return send_file(
                str(geojson_path),
                mimetype='application/geo+json',
                as_attachment=True,
                download_name=f'{project.name}.geojson'
            )
    
    return jsonify({
        'error': f'Export data not available for format: {format}'
    }), 404
