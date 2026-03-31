"""
Terra Pravah - Database Models
==============================
SQLAlchemy models for users, projects, teams, and analytics.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()


def generate_uuid():
    return str(uuid.uuid4())


# Association Tables
team_members = db.Table(
    'team_members',
    db.Column('team_id', db.String(36), db.ForeignKey('teams.id'), primary_key=True),
    db.Column('user_id', db.String(36), db.ForeignKey('users.id'), primary_key=True),
    db.Column('role', db.String(20), default='member'),  # admin, editor, viewer
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

project_collaborators = db.Table(
    'project_collaborators',
    db.Column('project_id', db.String(36), db.ForeignKey('projects.id'), primary_key=True),
    db.Column('user_id', db.String(36), db.ForeignKey('users.id'), primary_key=True),
    db.Column('permission', db.String(20), default='viewer'),  # owner, editor, commenter, viewer
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)


class User(db.Model):
    """User model for authentication and profile."""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    
    # Profile
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(500))
    company = db.Column(db.String(200))
    job_title = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    timezone = db.Column(db.String(50), default='UTC')
    language = db.Column(db.String(10), default='en')
    
    # Authentication
    oauth_provider = db.Column(db.String(20))  # google, github, null for email
    oauth_id = db.Column(db.String(255))
    email_verified = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(255))
    
    # Subscription
    subscription_plan = db.Column(db.String(20), default='free')
    subscription_status = db.Column(db.String(20), default='active')  # active, cancelled, past_due
    stripe_customer_id = db.Column(db.String(100))
    subscription_expires_at = db.Column(db.DateTime)
    
    # Usage Tracking
    storage_used_bytes = db.Column(db.BigInteger, default=0)
    api_calls_this_month = db.Column(db.Integer, default=0)
    projects_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    
    # Preferences (JSON)
    preferences = db.Column(db.JSON, default=dict)
    
    # Relationships
    owned_projects = db.relationship('Project', backref='owner', lazy='dynamic',
                                      foreign_keys='Project.owner_id')
    teams = db.relationship('Team', secondary=team_members, backref='members')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email.split('@')[0]
    
    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'company': self.company,
            'job_title': self.job_title,
            'subscription_plan': self.subscription_plan,
            'subscription_tier': self.subscription_plan,  # Alias for frontend compatibility
            'role': 'user',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_private:
            data.update({
                'email_verified': self.email_verified,
                'two_factor_enabled': self.two_factor_enabled,
                'storage_used_bytes': self.storage_used_bytes,
                'projects_count': self.projects_count,
                'preferences': self.preferences
            })
        return data


class Team(db.Model):
    """Team model for organization management."""
    __tablename__ = 'teams'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    
    # Settings
    default_project_visibility = db.Column(db.String(20), default='team')  # private, team, public
    require_2fa = db.Column(db.Boolean, default=False)
    allowed_domains = db.Column(db.JSON, default=list)  # Email domains allowed to join
    
    # Billing
    billing_email = db.Column(db.String(255))
    stripe_customer_id = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Owner
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    projects = db.relationship('Project', backref='team', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'logo_url': self.logo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'member_count': len(self.members)
        }


class Project(db.Model):
    """Project model for drainage analysis projects."""
    __tablename__ = 'projects'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(500))
    
    # Location
    location_name = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    bounding_box = db.Column(db.JSON)  # [minx, miny, maxx, maxy]
    epsg_code = db.Column(db.Integer)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, processing, completed, failed, archived
    visibility = db.Column(db.String(20), default='private')  # private, team, public
    
    # Configuration
    units = db.Column(db.String(10), default='metric')  # metric, imperial
    design_storm_years = db.Column(db.Integer, default=10)
    runoff_coefficient = db.Column(db.Float, default=0.5)
    flow_algorithm = db.Column(db.String(20), default='dinf')  # d8, dinf, mfd
    
    # Results Summary
    total_channels = db.Column(db.Integer, default=0)
    total_length_km = db.Column(db.Float, default=0)
    total_outlets = db.Column(db.Integer, default=0)
    peak_flow_m3s = db.Column(db.Float)
    primary_count = db.Column(db.Integer, default=0)
    secondary_count = db.Column(db.Integer, default=0)
    tertiary_count = db.Column(db.Integer, default=0)
    
    # Files
    dtm_file_path = db.Column(db.String(500))
    dtm_file_size = db.Column(db.BigInteger)
    results_path = db.Column(db.String(500))
    geojson_path = db.Column(db.String(500))
    visualization_path = db.Column(db.String(500))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Foreign Keys
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.String(36), db.ForeignKey('teams.id'))
    
    # Relationships
    collaborators = db.relationship('User', secondary=project_collaborators, backref='shared_projects')
    versions = db.relationship('ProjectVersion', backref='project', lazy='dynamic', order_by='desc(ProjectVersion.version)')
    comments = db.relationship('Comment', backref='project', lazy='dynamic')
    analysis_jobs = db.relationship('AnalysisJob', backref='project', lazy='dynamic')
    
    # Tags
    tags = db.Column(db.JSON, default=list)
    
    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'location_name': self.location_name,
            'status': self.status,
            'visibility': self.visibility,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'owner': self.owner.to_dict() if self.owner else None,
            'tags': self.tags or [],
            # Include key file and result info in basic response
            'dtm_file_path': self.dtm_file_path,
            'visualization_path': self.visualization_path,
            'total_channels': self.total_channels,
            'total_length_km': self.total_length_km,
            'total_outlets': self.total_outlets,
            'peak_flow_m3s': self.peak_flow_m3s,
            'primary_count': self.primary_count or 0,
            'secondary_count': self.secondary_count or 0,
            'tertiary_count': self.tertiary_count or 0,
        }
        if include_details:
            data.update({
                'latitude': self.latitude,
                'longitude': self.longitude,
                'bounding_box': self.bounding_box,
                'epsg_code': self.epsg_code,
                'units': self.units,
                'design_storm_years': self.design_storm_years,
                'runoff_coefficient': self.runoff_coefficient,
                'flow_algorithm': self.flow_algorithm,
                'dtm_file_size': self.dtm_file_size,
                'results_path': self.results_path,
                'geojson_path': self.geojson_path,
                'processed_at': self.processed_at.isoformat() if self.processed_at else None
            })
        return data
    
    def get_dtm_file_path(self):
        """Get the absolute DTM file path, handling both absolute and relative paths."""
        from pathlib import Path
        from backend.config import Config
        if self.dtm_file_path:
            path = Path(self.dtm_file_path)
            # If already absolute, return as-is
            if path.is_absolute():
                return path
            # Otherwise make it relative to UPLOAD_FOLDER
            return Path(Config.UPLOAD_FOLDER) / path
        return None
    
    def get_results_path(self):
        """Get the absolute results path, handling both absolute and relative paths."""
        from pathlib import Path
        from backend.config import Config
        if self.results_path:
            path = Path(self.results_path)
            if path.is_absolute():
                return path
            return Path(Config.RESULTS_FOLDER) / path
        return None
    
    def get_geojson_path(self):
        """Get the absolute geojson path, handling both absolute and relative paths."""
        from pathlib import Path
        from backend.config import Config
        if self.geojson_path:
            path = Path(self.geojson_path)
            if path.is_absolute():
                return path
            return Path(Config.RESULTS_FOLDER) / path
        return None


class ProjectVersion(db.Model):
    """Version control for project designs."""
    __tablename__ = 'project_versions'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200))  # Optional version name
    description = db.Column(db.Text)
    
    # Snapshot of configuration
    config_snapshot = db.Column(db.JSON)
    results_snapshot = db.Column(db.JSON)
    
    # Files
    geojson_path = db.Column(db.String(500))
    report_path = db.Column(db.String(500))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    created_by = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by.to_dict() if self.created_by else None
        }


class AnalysisJob(db.Model):
    """Background job tracking for analysis tasks."""
    __tablename__ = 'analysis_jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    
    # Job info
    job_type = db.Column(db.String(50), nullable=False)  # full_analysis, quick_analysis, export, report
    status = db.Column(db.String(20), default='queued')  # queued, processing, completed, failed, cancelled
    progress = db.Column(db.Integer, default=0)  # 0-100
    current_step = db.Column(db.String(100))
    
    # Configuration
    config = db.Column(db.JSON, default=dict)
    
    # Results
    result = db.Column(db.JSON)
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # User
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_by = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'job_type': self.job_type,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message if self.status == 'failed' else None
        }


class Comment(db.Model):
    """Comments on projects for collaboration."""
    __tablename__ = 'comments'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Content
    content = db.Column(db.Text, nullable=False)
    
    # Location reference (optional)
    location_x = db.Column(db.Float)
    location_y = db.Column(db.Float)
    element_id = db.Column(db.String(100))  # Reference to specific design element
    
    # Threading
    parent_id = db.Column(db.String(36), db.ForeignKey('comments.id'))
    
    # Status
    resolved = db.Column(db.Boolean, default=False)
    resolved_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id])
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_id])
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'user': self.user.to_dict() if self.user else None,
            'location_x': self.location_x,
            'location_y': self.location_y,
            'element_id': self.element_id,
            'parent_id': self.parent_id,
            'resolved': self.resolved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reply_count': len(self.replies)
        }


class Notification(db.Model):
    """User notifications."""
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Content
    type = db.Column(db.String(50), nullable=False)  # analysis_complete, comment_mention, project_shared, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    
    # Reference
    reference_type = db.Column(db.String(50))  # project, comment, team
    reference_id = db.Column(db.String(36))
    
    # Status
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    # Delivery
    email_sent = db.Column(db.Boolean, default=False)
    push_sent = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(db.Model):
    """Audit log for compliance and tracking."""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    
    # Actor
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    
    # Action
    action = db.Column(db.String(100), nullable=False)  # create, update, delete, view, export, share
    resource_type = db.Column(db.String(50))  # project, user, team
    resource_id = db.Column(db.String(36))
    
    # Details
    details = db.Column(db.JSON)
    changes = db.Column(db.JSON)  # Old and new values for updates
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User')


class APIKey(db.Model):
    """API keys for programmatic access."""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    key_hash = db.Column(db.String(255), nullable=False)
    prefix = db.Column(db.String(10), nullable=False)  # First 8 chars for identification
    
    # Permissions
    scopes = db.Column(db.JSON, default=list)  # read, write, delete
    
    # Usage
    last_used_at = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    
    # Status
    active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='api_keys')


class Subscription(db.Model):
    """Subscription and billing records."""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Plan
    plan = db.Column(db.String(20), nullable=False)
    billing_cycle = db.Column(db.String(10))  # monthly, yearly
    
    # Stripe
    stripe_subscription_id = db.Column(db.String(100))
    stripe_price_id = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, cancelled, past_due, trialing
    
    # Dates
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='subscriptions')
