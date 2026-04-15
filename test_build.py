import logging
from pathlib import Path
logging.basicConfig(level=logging.INFO)

from backend.services.dtm_builder import build_dtm

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
        "Add a sample file and rerun test_build.py"
    )

las_path = sample_files[0]
out_path = str(PROJECT_ROOT / 'test_dtm.tif')

try:
    print(f"Starting build with: {las_path}")
    build_dtm(
        las_path=str(las_path),
        output_tif=out_path,
        resolution=1.0,
        epsg='EPSG:32644'
    )
    print("Done!")
except Exception as e:
    import traceback
    print("Failed!")
    traceback.print_exc()
