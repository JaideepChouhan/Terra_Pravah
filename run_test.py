import requests
import json
import os
from pathlib import Path

BASE_URL = 'http://localhost:5000/api'

PROJECT_ROOT = Path(__file__).resolve().parent
SEARCH_DIRS = [
    PROJECT_ROOT / 'point_cloud_data',
    PROJECT_ROOT / 'Kitchener_lidar',
    PROJECT_ROOT / 'uploads',
]
sample_files = []
for directory in SEARCH_DIRS:
    if directory.exists():
        sample_files.extend(sorted(directory.rglob('*.las')))
        sample_files.extend(sorted(directory.rglob('*.laz')))
if not sample_files:
    raise FileNotFoundError(
        "No LAS/LAZ files found in point_cloud_data/, Kitchener_lidar/, or uploads/. "
        "Add one and rerun run_test.py"
    )
DATA_FILE = sample_files[0]

# 1. Register or Login
s = requests.Session()
email = 'test2@example.com'
password = 'Password123'

res = s.post(f'{BASE_URL}/auth/register', json={'name': 'test', 'email': email, 'password': password})
print("Register:", res.status_code, res.text)
if res.status_code == 400 and 'already exists' in res.text:
    print("User exists, proceeding to login...")

res = s.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': password})
print("Login:", res.status_code, res.text)
if res.status_code != 200:
    print("Login failed")
    exit(1)
token = res.json().get('access_token')

headers = {'Authorization': f'Bearer {token}'}

# 2. Create Project
res = s.post(f'{BASE_URL}/projects', headers=headers, json={
    'name': 'Test Project',
    'description': 'Description',
    'design_storm_years': 10,
    'runoff_coefficient': 0.5,
    'flow_algorithm': 'd8'
})
print("Create Project:", res.status_code, res.text)
if res.status_code not in (200, 201):
    print("Failed to create project")
    exit(1)
project_id = res.json().get('project', {}).get('id')
if not project_id:
    print("No project ID")
    exit(1)


# 3. Upload LAS
with open(DATA_FILE, 'rb') as f:
    files = {'file': f}
    data = {'project_id': project_id}
    print("Uploading...", end='', flush=True)
    res = s.post(f'{BASE_URL}/uploads/las', headers=headers, files=files, data=data)
print("Upload LAS:", res.status_code, res.text)
upload_info = res.json()
filename = upload_info['file']['name']

# 4. Build DTM
res = s.post(f'{BASE_URL}/uploads/build-dtm', headers=headers, json={
    'project_id': project_id,
    'filename': filename,
    'resolution': 1.0,
    'epsg': 'EPSG:32644'
})
print("Build DTM:", res.status_code, res.text)
