import requests
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
        "Add one and rerun run_test2.py"
    )
DATA_FILE = sample_files[0]

s = requests.Session()
email = 'test5@example.com'
password = 'Password123'

res = s.post(f'{BASE_URL}/auth/register', json={'name': 'test5', 'email': email, 'password': password})
print('Register:', res.status_code)

res = s.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': password})
print('Login:', res.status_code)

if res.status_code == 200:
    token = res.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}

    res = s.post(f'{BASE_URL}/projects', headers=headers, json={
        'name': 'Test Project',
        'description': 'Description',
        'design_storm_years': 10,
        'runoff_coefficient': 0.5,
        'flow_algorithm': 'd8'
    })
    print('Create:', res.status_code)

    if res.status_code in (200, 201):
        project_id = res.json().get('project', {}).get('id')
        
        with open(DATA_FILE, 'rb') as f:
            files = {'file': f}
            data = {'project_id': project_id}
            res = s.post(f'{BASE_URL}/uploads/las', headers=headers, files=files, data=data)
        
        if res.status_code == 200:
            filename = res.json()['file']['name']
            res = s.post(f'{BASE_URL}/uploads/build-dtm', headers=headers, json={
                'project_id': project_id,
                'filename': filename,
                'resolution': 1.0,
                'epsg': 'EPSG:32644'
            })
            
            with open('api_results.txt', 'w') as f:
                f.write(f"Final Build DTM result: {res.status_code}\n")
                f.write(res.text)

