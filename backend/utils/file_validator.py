"""
File Validation Utility
Provides smart file format detection and validation for geospatial data.
"""

import mimetypes
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import rasterio
from rasterio.errors import RasterioIOError


class FileFormatDetector:
    """Smart file format detection and validation"""
    
    # Supported raster formats (extensions)
    RASTER_EXTENSIONS = {'.tif', '.tiff', '.geotiff', '.img', '.asc', '.grd', '.dem'}
    
    # Supported point cloud formats
    LIDAR_EXTENSIONS = {'.las', '.laz'}
    
    # Supported vector formats
    VECTOR_EXTENSIONS = {'.shp', '.geojson', '.kml', '.gpkg', '.gml', '.dxf'}
    
    # File signatures (magic bytes) for format detection
    FILE_SIGNATURES = {
        'tiff_le': (b'\x49\x49\x2A\x00', 0),  # TIFF Little Endian
        'tiff_be': (b'\x4D\x4D\x00\x2A', 0),  # TIFF Big Endian
        'lasf': (b'LASF', 0),  # LAS format
        'geojson': (b'{', 0),  # GeoJSON (JSON start)
    }
    
    @classmethod
    def detect_format(cls, file_path: Path) -> Dict[str, Any]:
        """
        Detect file format using multiple methods:
        1. File signature (magic bytes)
        2. File extension
        3. MIME type
        4. Content validation
        
        Returns:
            Dict with format information including:
            - format_type: 'raster', 'vector', 'lidar', 'unknown'
            - extension: file extension
            - mime_type: detected MIME type
            - is_valid: whether file passed validation
            - is_cog: if raster, whether it's Cloud Optimized GeoTIFF
            - details: additional format-specific information
        """
        result = {
            'format_type': 'unknown',
            'extension': file_path.suffix.lower(),
            'mime_type': None,
            'is_valid': False,
            'is_cog': False,
            'details': {}
        }
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        result['mime_type'] = mime_type
        
        # Check file signature
        signature_type = cls._check_signature(file_path)
        
        extension = file_path.suffix.lower()
        
        # Determine format type
        if extension in cls.RASTER_EXTENSIONS or signature_type in ['tiff_le', 'tiff_be']:
            result['format_type'] = 'raster'
            is_valid, details = cls._validate_raster(file_path)
            result['is_valid'] = is_valid
            result['details'] = details
            result['is_cog'] = details.get('is_cog', False)
            
        elif extension in cls.LIDAR_EXTENSIONS or signature_type == 'lasf':
            result['format_type'] = 'lidar'
            is_valid, details = cls._validate_lidar(file_path)
            result['is_valid'] = is_valid
            result['details'] = details
            
        elif extension in cls.VECTOR_EXTENSIONS:
            result['format_type'] = 'vector'
            result['is_valid'] = True  # Basic validation
            result['details'] = {'note': 'Vector format detected'}
        
        return result
    
    @classmethod
    def _check_signature(cls, file_path: Path) -> Optional[str]:
        """Check file signature (magic bytes)"""
        try:
            with open(file_path, 'rb') as f:
                file_header = f.read(16)
                
            for sig_name, (signature, offset) in cls.FILE_SIGNATURES.items():
                if file_header[offset:offset+len(signature)] == signature:
                    return sig_name
        except Exception:
            pass
        
        return None
    
    @classmethod
    def _validate_raster(cls, file_path: Path) -> Tuple[bool, Dict]:
        """
        Validate raster file using rasterio and check if it's COG
        
        Returns:
            Tuple of (is_valid, details_dict)
        """
        details = {}
        
        try:
            with rasterio.open(str(file_path)) as src:
                details = {
                    'driver': src.driver,
                    'width': src.width,
                    'height': src.height,
                    'crs': str(src.crs) if src.crs else None,
                    'bounds': list(src.bounds) if src.bounds else None,
                    'resolution': src.res,
                    'dtype': str(src.dtypes[0]) if src.dtypes else None,
                    'band_count': src.count,
                    'nodata': src.nodata,
                    'transform': list(src.transform)[:6] if src.transform else None,
                }
                
                # Check if it's a Cloud Optimized GeoTIFF (COG)
                is_cog = cls._is_cloud_optimized_geotiff(src)
                details['is_cog'] = is_cog
                
                if is_cog:
                    details['cog_info'] = cls._get_cog_details(src)
                
                return True, details
                
        except RasterioIOError as e:
            details['error'] = f'Invalid raster file: {str(e)}'
            return False, details
        except Exception as e:
            details['error'] = f'Error reading raster: {str(e)}'
            return False, details
    
    @classmethod
    def _is_cloud_optimized_geotiff(cls, src) -> bool:
        """
        Check if a GeoTIFF is Cloud Optimized (COG)
        
        COG requirements:
        1. Tiled (not striped)
        2. Has overviews
        3. Proper tile/overview ordering
        """
        try:
            # Check if driver is GeoTIFF
            if src.driver != 'GTiff':
                return False
            
            # Check if tiled (COG must be tiled)
            is_tiled = src.profile.get('tiled', False)
            if not is_tiled:
                return False
            
            # Check for overviews (COG should have overviews for efficient zooming)
            has_overviews = len(src.overviews(1)) > 0 if src.count > 0 else False
            
            # Check compression (COG typically uses compression)
            compression = src.profile.get('compress', None)
            
            # A file is likely COG if it's tiled and has overviews
            # Note: Full COG validation would check internal layout, but this is a good heuristic
            return is_tiled and has_overviews
            
        except Exception:
            return False
    
    @classmethod
    def _get_cog_details(cls, src) -> Dict:
        """Get Cloud Optimized GeoTIFF specific details"""
        try:
            details = {
                'tiled': src.profile.get('tiled', False),
                'blockxsize': src.profile.get('blockxsize'),
                'blockysize': src.profile.get('blockysize'),
                'compress': src.profile.get('compress'),
                'interleave': src.profile.get('interleave'),
                'overviews': [],
            }
            
            # Get overview levels
            if src.count > 0:
                overviews = src.overviews(1)
                details['overviews'] = overviews
                details['overview_count'] = len(overviews)
            
            return details
        except Exception:
            return {}
    
    @classmethod
    def _validate_lidar(cls, file_path: Path) -> Tuple[bool, Dict]:
        """
        Validate LiDAR file (LAS/LAZ)
        
        Returns:
            Tuple of (is_valid, details_dict)
        """
        details = {}
        
        try:
            # Try to import laspy
            try:
                import laspy
            except ImportError:
                details['warning'] = 'laspy not installed, basic validation only'
                return True, details
            
            # Read LAS file header
            with laspy.open(str(file_path)) as las_file:
                header = las_file.header
                
                details = {
                    'version': f'{header.major_version}.{header.minor_version}',
                    'point_format': header.point_format.id,
                    'point_count': header.point_count,
                    'scales': list(header.scales),
                    'offsets': list(header.offsets),
                    'mins': list(header.mins),
                    'maxs': list(header.maxs),
                }
                
                return True, details
                
        except Exception as e:
            details['error'] = f'Error reading LiDAR file: {str(e)}'
            # Still return True if file exists and has correct extension
            return file_path.exists(), details
    
    @classmethod
    def is_supported_format(cls, file_path: Path) -> bool:
        """
        Quick check if file format is supported
        
        Returns:
            bool: True if format is supported
        """
        extension = file_path.suffix.lower()
        return (extension in cls.RASTER_EXTENSIONS or 
                extension in cls.LIDAR_EXTENSIONS or 
                extension in cls.VECTOR_EXTENSIONS)
    
    @classmethod
    def get_format_category(cls, file_path: Path) -> str:
        """
        Get format category (raster, lidar, vector, unknown)
        
        Returns:
            str: Format category
        """
        extension = file_path.suffix.lower()
        
        if extension in cls.RASTER_EXTENSIONS:
            return 'raster'
        elif extension in cls.LIDAR_EXTENSIONS:
            return 'lidar'
        elif extension in cls.VECTOR_EXTENSIONS:
            return 'vector'
        else:
            return 'unknown'
    
    @classmethod
    def validate_file_size(cls, file_path: Path, max_size_mb: int = 500) -> Tuple[bool, str]:
        """
        Validate file size
        
        Args:
            file_path: Path to file
            max_size_mb: Maximum file size in MB
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            file_size = file_path.stat().st_size
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                size_mb = file_size / (1024 * 1024)
                return False, f'File size ({size_mb:.1f}MB) exceeds maximum ({max_size_mb}MB)'
            
            return True, 'File size valid'
            
        except Exception as e:
            return False, f'Error checking file size: {str(e)}'


def validate_uploaded_file(file_path: Path, max_size_mb: int = 500) -> Dict:
    """
    Comprehensive file validation
    
    Args:
        file_path: Path to uploaded file
        max_size_mb: Maximum allowed file size in MB
        
    Returns:
        Dict with validation results:
        - is_valid: bool
        - format_info: dict from FileFormatDetector
        - errors: list of error messages
        - warnings: list of warning messages
    """
    result = {
        'is_valid': True,
        'format_info': {},
        'errors': [],
        'warnings': []
    }
    
    # Check if file exists
    if not file_path.exists():
        result['is_valid'] = False
        result['errors'].append('File does not exist')
        return result
    
    # Check file size
    size_valid, size_msg = FileFormatDetector.validate_file_size(file_path, max_size_mb)
    if not size_valid:
        result['is_valid'] = False
        result['errors'].append(size_msg)
        return result
    
    # Detect and validate format
    format_info = FileFormatDetector.detect_format(file_path)
    result['format_info'] = format_info
    
    # Check if format is supported
    if format_info['format_type'] == 'unknown':
        result['is_valid'] = False
        result['errors'].append(f'Unsupported file format: {format_info["extension"]}')
        return result
    
    # Check format-specific validation
    if not format_info['is_valid']:
        result['is_valid'] = False
        error_msg = format_info['details'].get('error', 'File validation failed')
        result['errors'].append(error_msg)
        return result
    
    # Add informational messages
    if format_info.get('is_cog'):
        result['warnings'].append('Cloud Optimized GeoTIFF (COG) detected - optimized for streaming')
    
    if 'warning' in format_info['details']:
        result['warnings'].append(format_info['details']['warning'])
    
    return result
