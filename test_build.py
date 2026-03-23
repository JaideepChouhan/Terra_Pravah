import logging
logging.basicConfig(level=logging.INFO)

from backend.services.dtm_builder import build_dtm

las_path = r'D:\GIT\Terra_Pravah\point_cloud_data\67169_5NKR_CHAKHIRASINGH.las'
out_path = 'test_dtm.tif'

try:
    print("Starting build...")
    build_dtm(
        las_path=las_path,
        output_tif=out_path,
        resolution=1.0,
        epsg='EPSG:32644'
    )
    print("Done!")
except Exception as e:
    import traceback
    print("Failed!")
    traceback.print_exc()
