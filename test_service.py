import logging
logging.basicConfig(level=logging.INFO)

from backend.services.dtm_builder_service import DTMBuilderService

las_path = r'D:\GIT\Terra_Pravah\point_cloud_data\67169_5NKR_CHAKHIRASINGH.las'
import shutil
import os

os.makedirs('test_uploads', exist_ok=True)
shutil.copy(las_path, 'test_uploads/test.las')

service = DTMBuilderService(
    upload_folder='test_uploads',
    results_folder='test_results'
)

print("Starting service.process_las...")
result = service.process_las('test.las', resolution=1.0, epsg='EPSG:32644')
print("Done!", result)
