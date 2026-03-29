import logging
from pathlib import Path
logging.basicConfig(level=logging.INFO)

from backend.services.dtm_builder_service import DTMBuilderService

import shutil
import os

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
        "Add a sample file and rerun test_service.py"
    )

las_path = sample_files[0]

os.makedirs('test_uploads', exist_ok=True)
shutil.copy(str(las_path), 'test_uploads/test.las')

service = DTMBuilderService(
    upload_folder='test_uploads',
    results_folder='test_results'
)

print("Starting service.process_las...")
result = service.process_las('test.las', resolution=1.0, epsg='EPSG:32644')
print("Done!", result)
