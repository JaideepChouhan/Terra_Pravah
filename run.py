#!/usr/bin/env python3
"""
Terra Pravah - Main Entry Point
================================
Commercial-grade AI-powered drainage design platform.

The backend Flask app serves the built frontend from frontend/dist/ folder.

Usage:
    python run.py                    # Run development server (serves frontend + backend)
    python run.py --production       # Run with production settings
    python run.py --init-db          # Initialize database
    python run.py --migrate          # Run migrations
    python run.py --dev              # Run with debug enabled
    python run.py --host 0.0.0.0     # Custom host (default: localhost)
    python run.py --port 8000        # Custom port (default: 5000)
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
    """Initialize the database with tables and optional seed data."""
    with app.app_context():
        from backend.models.models import User, db
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create default admin user only if configured via environment variables
        if app.config.get('CREATE_DEFAULT_ADMIN', False):
            admin_email = app.config.get('DEFAULT_ADMIN_EMAIL')
            admin_password = app.config.get('DEFAULT_ADMIN_PASSWORD')
            
            if admin_email and admin_password:
                admin = User.query.filter_by(email=admin_email).first()
                if not admin:
                    admin = User()
                    admin.email = admin_email
                    admin.first_name = 'Admin'
                    admin.last_name = 'User'
                    admin.email_verified = True
                    admin.subscription_plan = 'enterprise'
                    admin.set_password(admin_password)
                    db.session.add(admin)
                    db.session.commit()
                    print(f"✅ Default admin user created ({admin_email})")
                    print("   ⚠️  Configured via environment variables")
            else:
                print("⚠️  CREATE_DEFAULT_ADMIN is true, but admin credentials not provided")
                print("   Set DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD in .env file")
        
        print("✅ Database initialization complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Terra Pravah - Drainage Design Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Run complete stack (backend serves frontend)
  python run.py --dev              # Run with debug enabled
  python run.py --production       # Run in production mode
  python run.py --init-db          # Initialize database only
  python run.py --host 0.0.0.0     # Bind to all interfaces
  python run.py --port 8000        # Use custom port
                                     """
    )
    
    parser.add_argument('--production', action='store_true', help='Run in production mode')
    parser.add_argument('--init-db', action='store_true', help='Initialize the database')
    parser.add_argument('--migrate', action='store_true', help='Run database migrations')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--dev', action='store_true', help='Enable debug mode')
    
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
    
    # Handle database commands
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
    
    # Initialize database on startup
    print("📦 Initializing Database...")
    init_database(app)
    
    print("\n" + "=" * 65)
    
    # Print configuration info
    env_name = 'PRODUCTION' if args.production else 'DEVELOPMENT'
    print(f"  🌍 Environment: {env_name}")
    print(f"  🔗 Server: http://{args.host}:{args.port}")
    print(f"  🗄️  Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print(f"  🔐 Debug Mode: {'Enabled' if args.dev else 'Disabled'}")
    print(f"  📱 Frontend: Served from backend (frontend/dist/)")
    print("")
    print("=" * 65)
    print("")
    print(f"  ✅ APPLICATION READY")
    print("")
    print(f"  🌐 Open: http://{args.host}:{args.port}")
    print(f"  📚 API Docs: http://{args.host}:{args.port}/api/docs")
    print(f"  🏥 Health Check: http://{args.host}:{args.port}/api/health")
    print("")
    print("  Press Ctrl+C to stop the server")
    print("")
    
    # Run the server
    try:
        from backend.app import socketio
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.dev or (not args.production),
            allow_unsafe_werkzeug=True
        )
    except ImportError:
        # Fallback if socketio not available
        app.run(
            host=args.host,
            port=args.port,
            debug=args.dev or (not args.production)
        )


if __name__ == '__main__':
    main()