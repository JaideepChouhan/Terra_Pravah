"""Test imports to verify backend can start"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

try:
    print("Testing file_validator import...")
    from backend.utils.file_validator import FileFormatDetector, validate_uploaded_file
    print("✓ file_validator imported successfully")
    
    print("\nTesting config import...")
    from backend.config import Config
    print("✓ config imported successfully")
    
    print("\nTesting models import...")
    from backend.models.models import db, User, Project
    print("✓ models imported successfully")
    
    print("\nTesting uploads API import...")
    from backend.api.uploads import uploads_bp
    print("✓ uploads API imported successfully")
    
    print("\nTesting projects API import...")
    from backend.api.projects import projects_bp
    print("✓ projects API imported successfully")
    
    print("\n✅ All imports successful! Backend should start properly.")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
