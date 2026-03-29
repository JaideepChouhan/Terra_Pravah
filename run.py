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
import shutil
import subprocess
import atexit
from pathlib import Path

# Add the backend directory to the path
BACKEND_DIR = Path(__file__).parent / 'backend'
sys.path.insert(0, str(BACKEND_DIR))


PROJECT_ROOT = Path(__file__).resolve().parent


def ensure_project_python():
    """Re-exec with project venv Python when available and not already active."""
    venv_python = PROJECT_ROOT / '.venv' / 'bin' / 'python'
    venv_root = (PROJECT_ROOT / '.venv').resolve()
    if not venv_python.exists():
        return

    # Compare environment prefixes because venv Python may be a symlink to system python.
    current_prefix = Path(sys.prefix).resolve()
    if current_prefix == venv_root:
        return

    if os.getenv('TERRA_PRAVAH_REEXEC') == '1':
        return

    print(f"🔁 Switching to project Python: {venv_python}")
    env = os.environ.copy()
    env['TERRA_PRAVAH_REEXEC'] = '1'
    os.execvpe(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]], env)


def normalize_database_url():
    """Normalize relative SQLite URLs to absolute project-root paths."""
    raw_url = os.getenv('DATABASE_URL', '').strip()
    if not raw_url:
        return

    if raw_url == 'sqlite:///:memory:':
        return

    if not raw_url.startswith('sqlite:///'):
        return

    sqlite_path = raw_url[len('sqlite:///'):]
    if not sqlite_path:
        return

    # sqlite:////absolute/path.db -> sqlite_path starts with '/'
    # sqlite:///relative/path.db -> make it absolute from project root
    if sqlite_path.startswith('/'):
        db_file = Path(sqlite_path)
    else:
        db_file = (PROJECT_ROOT / sqlite_path).resolve()
        os.environ['DATABASE_URL'] = f"sqlite:///{db_file}"

    try:
        db_file.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        safe_url = force_safe_sqlite_url()
        print(f"⚠️  DATABASE_URL path is not writable, using fallback: {safe_url}")


def force_safe_sqlite_url():
    """Force DATABASE_URL to a safe absolute sqlite file in the project."""
    safe_db = (PROJECT_ROOT / 'database' / 'terrapravah.db').resolve()
    safe_db.parent.mkdir(parents=True, exist_ok=True)
    safe_url = f"sqlite:///{safe_db}"
    os.environ['DATABASE_URL'] = safe_url
    return safe_url


def start_frontend_dev(frontend_port=3000):
    """Start Vite dev server as a background subprocess."""
    frontend_dir = PROJECT_ROOT / 'frontend'
    npm_cmd = shutil.which('npm')

    if not frontend_dir.exists():
        print("⚠️  Frontend directory not found, skipping frontend dev server startup")
        return None

    if not npm_cmd:
        print("⚠️  npm not found in PATH, skipping frontend dev server startup")
        return None

    node_modules = frontend_dir / 'node_modules'
    if not node_modules.exists():
        print("⚠️  frontend/node_modules not found. Run 'cd frontend && npm install' first")
        return None

    try:
        process = subprocess.Popen(
            [npm_cmd, 'run', 'dev', '--', '--host', '0.0.0.0', '--port', str(frontend_port)],
            cwd=str(frontend_dir),
            stdout=None,
            stderr=None
        )
        print(f"✅ Frontend dev server started on http://localhost:{frontend_port} (pid: {process.pid})")

        def _cleanup():
            if process.poll() is None:
                process.terminate()

        atexit.register(_cleanup)
        return process
    except Exception as exc:
        print(f"⚠️  Failed to start frontend dev server: {exc}")
        return None


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
    ensure_project_python()

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
    parser.add_argument('--frontend-dev', action='store_true', help='Also start frontend Vite dev server')
    parser.add_argument('--frontend-port', type=int, default=3000, help='Frontend dev server port (default: 3000)')
    
    args = parser.parse_args()
    
    # Set environment
    if args.production:
        os.environ['FLASK_ENV'] = 'production'
        config_name = 'production'
    else:
        os.environ['FLASK_ENV'] = 'development'
        config_name = 'development'
    
    # Normalize DB URL before importing app config (which is evaluated at import time).
    normalize_database_url()

    from backend.app import create_app, socketio

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
    try:
        init_database(app)
    except Exception as exc:
        error_text = str(exc).lower()
        if 'unable to open database file' in error_text:
            print(f"⚠️  Database initialization failed: {exc}")
            safe_url = force_safe_sqlite_url()
            print(f"🔁 Retrying with safe database path: {safe_url}")
            try:
                app = create_app(config_name)
                init_database(app)
            except Exception as retry_exc:
                print(f"❌ Database initialization failed after retry: {retry_exc}")
                print("   Check file permissions for the project and database directories.")
                sys.exit(1)
        else:
            print(f"❌ Database initialization failed: {exc}")
            print("   Check DATABASE_URL in .env. For SQLite, prefer a project-absolute path.")
            print("   Example: DATABASE_URL=sqlite:////home/USER/project/database/terrapravah.db")
            sys.exit(1)

    frontend_process = None
    if args.frontend_dev:
        frontend_process = start_frontend_dev(args.frontend_port)
    
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
    if frontend_process:
        print(f"  💻 Frontend Dev: http://localhost:{args.frontend_port}")
    print(f"  📚 API Docs: http://{args.host}:{args.port}/api/docs")
    print(f"  🏥 Health Check: http://{args.host}:{args.port}/api/health")
    print("")
    print("  Press Ctrl+C to stop the server")
    print("")
    
    # Run the server
    socketio.run(
        app,
        host=args.host,
        port=args.port,
        debug=args.dev or (not args.production),
        allow_unsafe_werkzeug=True
    )


if __name__ == '__main__':
    main()