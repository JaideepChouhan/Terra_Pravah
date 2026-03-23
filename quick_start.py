"""
Quick Start Script - Terra Pravah with Testing
===============================================
This script helps you quickly start the application and verify it's working.
"""

import sys
import subprocess
from pathlib import Path
import time

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"Running: {description}")
    print(f"Command: {cmd}\n")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0

def main():
    print_section("Terra Pravah - Quick Start & Verification")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    print(f"Project directory: {project_dir}\n")
    
    # Step 1: Verify backend can start
    print_section("Step 1: Verifying Backend Modules")
    if not run_command("python verify_backend.py", "Backend verification"):
        print("\n❌ Backend verification failed!")
        print("Please fix the errors above before continuing.\n")
        return False
    
    print("\n✅ Backend verification passed!\n")
    time.sleep(2)
    
    # Step 2: Check if .env exists
    print_section("Step 2: Checking Configuration")
    env_file = project_dir / '.env'
    
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("\nCreating .env from template...")
        
        env_example = project_dir / '.env.example'
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Created .env file")
            print("\n⚠️  IMPORTANT: Edit .env to configure admin user (optional)")
            print("   Uncomment and set:")
            print("   CREATE_DEFAULT_ADMIN=true")
            print("   DEFAULT_ADMIN_EMAIL=your@email.com")
            print("   DEFAULT_ADMIN_PASSWORD=YourPassword\n")
        else:
            print("❌ .env.example not found!")
            return False
    else:
        print("✅ .env file exists\n")
    
    time.sleep(2)
    
    # Step 3: Check database
    print_section("Step 3: Checking Database")
    db_file = project_dir / 'database' / 'terrapravah.db'
    
    if not db_file.exists():
        print("Database not found. Initializing...")
        if not run_command("python run.py --init-db", "Database initialization"):
            print("❌ Database initialization failed!")
            return False
        print("✅ Database initialized\n")
    else:
        print(f"✅ Database exists: {db_file}\n")
    
    time.sleep(2)
    
    # Step 4: Check test file
    print_section("Step 4: Checking Test LAS File")
    test_file = project_dir / 'point_cloud_data' / '67169_5NKR_CHAKHIRASINGH.las'
    
    if test_file.exists():
        size_mb = test_file.stat().st_size / (1024 * 1024)
        print(f"✅ Test LAS file found")
        print(f"   Path: {test_file}")
        print(f"   Size: {size_mb:.2f} MB\n")
    else:
        print(f"⚠️  Test LAS file not found at: {test_file}")
        print("   You can still test with other files\n")
    
    time.sleep(2)
    
    # Step 5: Ready to start
    print_section("Ready to Start!")
    
    print("✅ All checks passed! You can now start the application.\n")
    
    print("To start the development server:")
    print("  python run.py --dev\n")
    
    print("The server will be available at:")
    print("  http://localhost:5000\n")
    
    print("Testing workflow:")
    print("  1. Open http://localhost:5000 in your browser")
    print("  2. Register a new account or login")
    print("  3. Click 'New Project'")
    print("  4. Fill in project details")
    if test_file.exists():
        print(f"  5. Upload test file: {test_file.name}")
    else:
        print("  5. Upload a GeoTIFF or LAS file")
    print("  6. Click 'Create Project'")
    print("  7. Verify project is created successfully\n")
    
    print("Documentation:")
    print("  - Session files: C:\\Users\\shail\\.copilot\\session-state\\26dc7a85-c6c7-4760-9278-72734f2abf7a\\files\\")
    print("  - MANUAL_TEST_GUIDE.md - Complete testing guide")
    print("  - PROJECT_FIX_SUMMARY.md - What was fixed")
    print("  - DEBUG_LOG.md - Debugging information\n")
    
    print("="*70)
    
    # Ask if user wants to start server now
    response = input("\nWould you like to start the development server now? (y/n): ")
    
    if response.lower() == 'y':
        print("\nStarting server...")
        print("Press Ctrl+C to stop the server\n")
        subprocess.run("python run.py --dev", shell=True)
    else:
        print("\nTo start later, run: python run.py --dev\n")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
