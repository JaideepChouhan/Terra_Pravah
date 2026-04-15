"""
Verify Backend Can Start
=========================
Quick check to ensure the backend can start without import errors.
"""

import sys
import os
from pathlib import Path

def ensure_project_python():
    """Ensure we are running with the project's virtual environment python"""
    project_dir = Path(__file__).parent.absolute()
    
    # Simple check: are we in ANY virtual environment?
    in_venv = sys.prefix != sys.base_prefix
    
    # If not in a venv, try to find one and restart
    if not in_venv:
        venv_python_linux = project_dir / '.venv' / 'bin' / 'python'
        venv_python_win = project_dir / '.venv' / 'Scripts' / 'python.exe'
        
        python_exe = None
        if venv_python_win.exists():
            python_exe = str(venv_python_win)
        elif venv_python_linux.exists():
            python_exe = str(venv_python_linux)
            
        if python_exe:
            print(f"🔄 Restarting using virtual environment: {python_exe}")
            os.execv(python_exe, [python_exe] + sys.argv)

def main():
    ensure_project_python()
    
    print("=" * 60)
    print("Terra Pravah - Backend Startup Verification")
    print("=" * 60)
    
    # Add backend to path
    backend_dir = Path(__file__).parent / 'backend'
    sys.path.insert(0, str(backend_dir))
    
    print("\n1. Testing Core Imports...")
    try:
        from backend.config import Config, get_config
        print("   ✓ Config module")
    except Exception as e:
        print(f"   ✗ Config module failed: {e}")
        return False
    
    try:
        from backend.models.models import db, User, Project
        print("   ✓ Models module")
    except Exception as e:
        print(f"   ✗ Models module failed: {e}")
        return False
    
    print("\n2. Testing Utility Modules...")
    try:
        from backend.utils.file_validator import FileFormatDetector, validate_uploaded_file
        print("   ✓ File validator module")
        
        # Test that the class works
        test_path = Path("test.tif")
        result = FileFormatDetector.is_supported_format(test_path)
        print(f"   ✓ FileFormatDetector methods work (test: {result})")
    except Exception as e:
        print(f"   ✗ File validator failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n3. Testing API Blueprints...")
    try:
        from backend.api.uploads import uploads_bp
        print("   ✓ Uploads API blueprint")
    except Exception as e:
        print(f"   ✗ Uploads API failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from backend.api.projects import projects_bp
        print("   ✓ Projects API blueprint")
    except Exception as e:
        print(f"   ✗ Projects API failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from backend.api.analysis import analysis_bp
        print("   ✓ Analysis API blueprint")
    except Exception as e:
        print(f"   ✗ Analysis API failed: {e}")
        return False
    
    print("\n4. Testing Flask App Creation...")
    try:
        from backend.app import create_app
        print("   ✓ App factory imported")
        
        # Try to create app (development mode)
        app = create_app('development')
        print(f"   ✓ App created successfully")
        print(f"   - App name: {app.name}")
        print(f"   - Debug mode: {app.debug}")
        
        with app.app_context():
            print(f"   ✓ App context works")
            
    except Exception as e:
        print(f"   ✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n5. Checking Dependencies...")
    try:
        import rasterio
        print(f"   ✓ rasterio {rasterio.__version__}")
    except:
        print("   ⚠ rasterio not available")
    
    try:
        import laspy
        print(f"   ✓ laspy {laspy.__version__}")
    except:
        print("   ⚠ laspy not available (optional for LAS files)")
    
    try:
        import flask
        print(f"   ✓ Flask {flask.__version__}")
    except:
        print("   ✗ Flask not available (REQUIRED)")
        return False
    
    try:
        import sqlalchemy
        print(f"   ✓ SQLAlchemy {sqlalchemy.__version__}")
    except:
        print("   ✗ SQLAlchemy not available (REQUIRED)")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL CHECKS PASSED - Backend is ready to start!")
    print("=" * 60)
    print("\nYou can now run:")
    print("  python run.py --dev")
    print("\nOr initialize the database first:")
    print("  python run.py --init-db")
    print()
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
