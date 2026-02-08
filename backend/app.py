"""
Terra Pravah - Main Application Factory
========================================
Flask application factory with all extensions and blueprints.
"""

import os
import logging
from pathlib import Path
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

from backend.config import get_config, config as config_map
from backend.models.models import db

# Initialize extensions
jwt = JWTManager()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO()


def create_app(config_name=None):
    """Application factory."""
    
    # Determine static folder - Vite uses 'dist', fallback to checking both
    base_path = Path(__file__).parent.parent
    dist_folder = base_path / 'frontend' / 'dist'
    build_folder = base_path / 'frontend' / 'build'
    
    if dist_folder.exists():
        static_folder = str(dist_folder)
    elif build_folder.exists():
        static_folder = str(build_folder)
    else:
        # Use dist as default (will be created on build)
        static_folder = str(dist_folder)
    
    app = Flask(__name__, 
                static_folder=static_folder,
                static_url_path='')
    
    # Load configuration
    if config_name is None:
        config_class = get_config()
    elif isinstance(config_name, str):
        # Look up config class from name
        config_class = config_map.get(config_name, config_map['default'])
    else:
        # Assume it's already a config class
        config_class = config_name
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']),
         supports_credentials=True)
    
    # Create required directories
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    Path(app.config['RESULTS_FOLDER']).mkdir(parents=True, exist_ok=True)
    
    # Create database directory if using SQLite
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        db_path = Path(db_uri.replace('sqlite:///', ''))
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    # JWT callbacks
    register_jwt_callbacks(app)
    
    # Health check
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': app.config.get('APP_VERSION', '2.0.0')
        })
    
    # Serve frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        # Check if static folder exists and has index.html
        if not app.static_folder or not Path(app.static_folder).exists():
            return jsonify({
                'message': 'Terra Pravah API Server',
                'status': 'running',
                'note': 'Frontend not built. Run "cd frontend && npm run build" or access the dev server at http://localhost:5173',
                'api_docs': '/api/docs',
                'health': '/health'
            })
        
        index_path = Path(app.static_folder) / 'index.html'
        if not index_path.exists():
            return jsonify({
                'message': 'Terra Pravah API Server',
                'status': 'running',
                'note': 'Frontend not built. Run "cd frontend && npm run build" or access the dev server at http://localhost:5173',
                'api_docs': '/api/docs',
                'health': '/health'
            })
        
        if path and Path(app.static_folder, path).exists():
            return app.send_static_file(path)
        return app.send_static_file('index.html')
    
    return app


def setup_logging(app):
    """Configure logging."""
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Set Flask logger level
    app.logger.setLevel(log_level)


def register_blueprints(app):
    """Register all API blueprints."""
    from backend.api.auth import auth_bp
    from backend.api.users import users_bp
    from backend.api.projects import projects_bp
    from backend.api.analysis import analysis_bp
    from backend.api.teams import teams_bp
    from backend.api.uploads import uploads_bp
    from backend.api.reports import reports_bp
    from backend.api.billing import billing_bp
    from backend.api.admin import admin_bp
    
    # API routes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(teams_bp, url_prefix='/api/teams')
    app.register_blueprint(uploads_bp, url_prefix='/api/uploads')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(billing_bp, url_prefix='/api/billing')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Health check endpoint
    @app.route('/api/health')
    def api_health():
        return jsonify({'status': 'healthy', 'version': app.config.get('APP_VERSION', '2.0.0')})


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500


def register_commands(app):
    """Register CLI commands."""
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command('seed-db')
    def seed_db():
        """Seed the database with sample data."""
        from backend.utils.seed import seed_database
        seed_database()
        print('Database seeded.')


def register_jwt_callbacks(app):
    """Register JWT callbacks."""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token Expired',
            'message': 'Your session has expired. Please log in again.'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid Token',
            'message': 'Invalid authentication token.'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization Required',
            'message': 'Authentication token is missing.'
        }), 401
