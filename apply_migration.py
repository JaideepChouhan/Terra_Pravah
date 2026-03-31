#!/usr/bin/env python3
"""Apply database migration to add cog_path column."""

import os
import sys
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)
PROJECT_ROOT = Path(__file__).parent

# Add the backend directory to the path
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

# Normalize database URL and ensure directory exists (from run.py)
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
        safe_db = (PROJECT_ROOT / 'database' / 'terrapravah.db').resolve()
        safe_db.parent.mkdir(parents=True, exist_ok=True)
        os.environ['DATABASE_URL'] = f"sqlite:///{safe_db}"

# Normalize database URL first
normalize_database_url()

# Make sure database directory exists
db_path = PROJECT_ROOT / 'database'
db_path.mkdir(parents=True, exist_ok=True)

from backend.app import create_app
from backend.models.models import db

app = create_app('development')

with app.app_context():
    try:
        # First, create all tables if they don't exist
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created/verified")
        
        # Now check and add cog_path column if needed
        with db.engine.connect() as conn:
            # Check if column exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('projects')]
            
            if 'cog_path' not in columns:
                print("Adding cog_path column to projects table...")
                conn.execute(db.text("""
                    ALTER TABLE projects ADD COLUMN cog_path VARCHAR(500)
                """))
                conn.commit()
                print("✅ Successfully added cog_path column to projects table")
            else:
                print("✓ cog_path column already exists in projects table")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
