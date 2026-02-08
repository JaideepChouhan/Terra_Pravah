#!/usr/bin/env python3
"""
Terra Pravah - Main Entry Point
================================
Commercial-grade AI-powered drainage design platform.

Usage:
    python run.py                    # Run development server
    python run.py --production       # Run with production settings
    python run.py --init-db          # Initialize database
    python run.py --migrate          # Run migrations
"""

import os
import sys
import argparse
from pathlib import Path

# Add the backend directory to the path
BACKEND_DIR = Path(__file__).parent / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

from backend.app import create_app, db


def init_database(app):
    """Initialize the database with tables and seed data."""
    with app.app_context():
        from backend.models.models import User, db
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create default admin user if doesn't exist
        admin = User.query.filter_by(email='admin@terrapravah.com').first()
        if not admin:
            admin = User()
            admin.email = 'admin@terrapravah.com'
            admin.first_name = 'Admin'
            admin.last_name = 'User'
            admin.email_verified = True
            admin.subscription_plan = 'enterprise'
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created (admin@terrapravah.com / admin123)")
            print("   ⚠️  Please change the admin password immediately!")
        
        print("✅ Database initialization complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Terra Pravah - Drainage Design Platform')
    parser.add_argument('--production', action='store_true', help='Run in production mode')
    parser.add_argument('--init-db', action='store_true', help='Initialize the database')
    parser.add_argument('--migrate', action='store_true', help='Run database migrations')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Set environment
    if args.production:
        os.environ['FLASK_ENV'] = 'production'
        config_name = 'production'
    else:
        os.environ['FLASK_ENV'] = 'development'
        config_name = 'development'
    
    # Create the app
    app = create_app(config_name)
    
    # Handle commands
    if args.init_db:
        init_database(app)
        return
    
    if args.migrate:
        from flask_migrate import upgrade
        with app.app_context():
            upgrade()
            print("✅ Migrations applied successfully")
        return
    
    # Display startup banner
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ████████╗███████╗██████╗ ██████╗  █████╗                  ║
║     ╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗                 ║
║        ██║   █████╗  ██████╔╝██████╔╝███████║                 ║
║        ██║   ██╔══╝  ██╔══██╗██╔══██╗██╔══██║                 ║
║        ██║   ███████╗██║  ██║██║  ██║██║  ██║                 ║
║        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝                 ║
║                                                               ║
║     ██████╗ ██████╗  █████╗ ██╗   ██╗ █████╗ ██╗  ██╗         ║
║     ██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔══██╗██║  ██║         ║
║     ██████╔╝██████╔╝███████║██║   ██║███████║███████║         ║
║     ██╔═══╝ ██╔══██╗██╔══██║╚██╗ ██╔╝██╔══██║██╔══██║         ║
║     ██║     ██║  ██║██║  ██║ ╚████╔╝ ██║  ██║██║  ██║         ║
║     ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝         ║
║                                                               ║
║           AI-Powered Drainage Design Platform                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Print configuration info
    print(f"  🌍 Environment: {config_name}")
    print(f"  🔗 Server: http://{args.host}:{args.port}")
    print(f"  🗄️  Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print(f"  🔐 Debug Mode: {'Enabled' if args.debug else 'Disabled'}")
    print("")
    print("  📚 API Documentation: http://localhost:{}/api/docs".format(args.port))
    print("  🏥 Health Check: http://localhost:{}/api/health".format(args.port))
    print("")
    print("  Press Ctrl+C to stop the server")
    print("=" * 65)
    print("")
    
    # Run the server
    try:
        from backend.app import socketio
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug or (not args.production),
            allow_unsafe_werkzeug=True
        )
    except ImportError:
        # Fallback if socketio not available
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or (not args.production)
        )

if __name__ == '__main__':
    main()