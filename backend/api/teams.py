"""
Terra Pravah - Teams API
========================
Team management and collaboration.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import re

from backend.models.models import db, Team, User, AuditLog

teams_bp = Blueprint('teams', __name__)


def generate_slug(name):
    """Generate a URL-safe slug from team name."""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug[:50]


@teams_bp.route('', methods=['GET'])
@jwt_required()
def list_teams():
    """List teams the user belongs to."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'teams': [t.to_dict() for t in user.teams]
    })


@teams_bp.route('', methods=['POST'])
@jwt_required()
def create_team():
    """Create a new team."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Team name is required'}), 400
    
    # Generate unique slug
    base_slug = generate_slug(name)
    slug = base_slug
    counter = 1
    
    while Team.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    team = Team(
        name=name,
        slug=slug,
        description=data.get('description'),
        owner_id=user_id,
        billing_email=user.email
    )
    
    db.session.add(team)
    
    # Add creator as admin member
    team.members.append(user)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Team created successfully',
        'team': team.to_dict()
    }), 201


@teams_bp.route('/<team_id>', methods=['GET'])
@jwt_required()
def get_team(team_id):
    """Get team details."""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    # Check membership
    user = User.query.get(user_id)
    if team not in user.teams:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'team': team.to_dict(),
        'members': [m.to_dict() for m in team.members]
    })


@teams_bp.route('/<team_id>', methods=['PUT'])
@jwt_required()
def update_team(team_id):
    """Update team settings."""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    if team.owner_id != user_id:
        return jsonify({'error': 'Only the owner can update team settings'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        team.name = data['name'].strip()
    if 'description' in data:
        team.description = data['description']
    if 'logo_url' in data:
        team.logo_url = data['logo_url']
    if 'default_project_visibility' in data:
        team.default_project_visibility = data['default_project_visibility']
    if 'require_2fa' in data:
        team.require_2fa = data['require_2fa']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Team updated successfully',
        'team': team.to_dict()
    })


@teams_bp.route('/<team_id>', methods=['DELETE'])
@jwt_required()
def delete_team(team_id):
    """Delete a team."""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    if team.owner_id != user_id:
        return jsonify({'error': 'Only the owner can delete the team'}), 403
    
    db.session.delete(team)
    db.session.commit()
    
    return jsonify({
        'message': 'Team deleted successfully'
    })


@teams_bp.route('/<team_id>/members', methods=['GET'])
@jwt_required()
def list_members(team_id):
    """List team members."""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    user = User.query.get(user_id)
    if team not in user.teams:
        return jsonify({'error': 'Access denied'}), 403
    
    members = [{
        'user': m.to_dict(),
        'role': 'owner' if m.id == team.owner_id else 'member'
    } for m in team.members]
    
    return jsonify({
        'members': members
    })


@teams_bp.route('/<team_id>/members', methods=['POST'])
@jwt_required()
def invite_member(team_id):
    """Invite a user to the team."""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    if team.owner_id != user_id:
        return jsonify({'error': 'Only the owner can invite members'}), 403
    
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Find user
    invited_user = User.query.filter_by(email=email).first()
    
    if not invited_user:
        return jsonify({'error': 'User not found'}), 404
    
    if invited_user in team.members:
        return jsonify({'error': 'User is already a team member'}), 409
    
    # Add to team
    team.members.append(invited_user)
    db.session.commit()
    
    # TODO: Send invitation email
    
    return jsonify({
        'message': 'Member added successfully',
        'member': invited_user.to_dict()
    })


@teams_bp.route('/<team_id>/members/<member_id>', methods=['DELETE'])
@jwt_required()
def remove_member(team_id, member_id):
    """Remove a member from the team."""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    # Only owner can remove others, anyone can leave
    if team.owner_id != user_id and member_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if member_id == team.owner_id:
        return jsonify({'error': 'Cannot remove the team owner'}), 400
    
    member = User.query.get(member_id)
    if not member or member not in team.members:
        return jsonify({'error': 'Member not found'}), 404
    
    team.members.remove(member)
    db.session.commit()
    
    return jsonify({
        'message': 'Member removed successfully'
    })


@teams_bp.route('/<team_id>/projects', methods=['GET'])
@jwt_required()
def list_team_projects(team_id):
    """List projects belonging to a team."""
    user_id = get_jwt_identity()
    team = Team.query.get(team_id)
    
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    user = User.query.get(user_id)
    if team not in user.teams:
        return jsonify({'error': 'Access denied'}), 403
    
    projects = team.projects.all()
    
    return jsonify({
        'projects': [p.to_dict() for p in projects]
    })
