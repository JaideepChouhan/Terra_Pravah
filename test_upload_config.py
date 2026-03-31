#!/usr/bin/env python3
"""
Test upload configuration to ensure 5GB limit is properly configured.
"""
import os
import sys
from pathlib import Path

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import Config
from backend.app import create_app

print("=" * 70)
print("UPLOAD CONFIGURATION DIAGNOSTICS")
print("=" * 70)

# 1. Check environment variables
env_size = os.getenv('MAX_FILE_SIZE_MB')
print(f"\n1. Environment Variable (from .env):")
print(f"   MAX_FILE_SIZE_MB = {env_size}")

# 2. Check Config class
config = Config()
print(f"\n2. Config Class Values:")
print(f"   MAX_FILE_SIZE_MB = {config.MAX_FILE_SIZE_MB} MB")
print(f"   MAX_CONTENT_LENGTH = {config.MAX_CONTENT_LENGTH:,} bytes")
print(f"   MAX_CONTENT_LENGTH = {config.MAX_CONTENT_LENGTH / (1024**3):.2f} GB")

# 3. Check Flask app  
app = create_app()
print(f"\n3. Flask App Configuration:")
flask_mcl = app.config.get('MAX_CONTENT_LENGTH', 0)
flask_mfsm = app.config.get('MAX_FILE_SIZE_MB', 0)
print(f"   MAX_CONTENT_LENGTH = {flask_mcl:,} bytes")
print(f"   MAX_CONTENT_LENGTH = {flask_mcl / (1024**3):.2f} GB")
print(f"   MAX_FILE_SIZE_MB = {flask_mfsm} MB")

# 4. Test with actual files
print(f"\n4. File Size Tests (from /home/jaideepchouhan/Documents):")
test_dir = "/home/jaideepchouhan/Documents/AIR Docs/GSI 2026/Data/Zip files/Gujrat_Point_Cloud"
if Path(test_dir).exists():
    for file_path in Path(test_dir).glob("*"):
        if file_path.is_file():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            size_bytes = file_path.stat().st_size
            max_bytes = config.MAX_CONTENT_LENGTH
            status = "✓ PASS" if size_bytes <= max_bytes else "✗ FAIL"
            print(f"   {file_path.name}")
            print(f"      Size: {size_mb:.1f} MB ({size_bytes:,} bytes)")
            print(f"      Status: {status}")
else:
    print(f"   Test directory not found: {test_dir}")

# 5. Validation function test
print(f"\n5. Backend Validation Function Test:")
from backend.utils.file_validator import FileFormatDetector

test_sizes = [1800, 1600]
for test_mb in test_sizes:
    test_bytes = test_mb * 1024 * 1024
    is_valid, msg = FileFormatDetector.validate_file_size(Path("/tmp/dummy.las"), config.MAX_FILE_SIZE_MB)
    print(f"   {test_mb}MB file: {msg}")

print("\n" + "=" * 70)
print("Conclusion:")
if env_size == "5000" and config.MAX_FILE_SIZE_MB == 5000:
    print("✓ Configuration is correct - 5GB upload limit is enabled")
else:
    print("✗ Configuration mismatch - Check .env file and restart the application")
print("=" * 70)
