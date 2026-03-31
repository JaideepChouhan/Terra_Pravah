"""
Terra Pravah - Export Service
=============================
Handles exporting geospatial data in various formats with emphasis on Cloud Optimized GeoTIFF (COG).
Provides utilities for converting DTM, drainage networks, and analysis results to portable formats.
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union
from datetime import datetime
import logging

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.enums import Resampling
from rasterio.shutil import copy as rio_copy
import geopandas as gpd
from shapely.geometry import LineString, mapping

logger = logging.getLogger(__name__)


class GeoTIFFExporter:
    """
    Export geospatial data as Cloud Optimized GeoTIFF (COG) with compression and tiling.
    
    Features:
    - Automatic COG creation with embedded overviews
    - Compression options (deflate, lzw, zstd)
    - Multi-band support (RGB hillshade, etc.)
    - Metadata preservation
    - Progress tracking
    
    References:
    - https://www.cogeo.org/ (Cloud Optimized GeoTIFF specification)
    """
    
    DEFAULT_BLOCK_SIZE = 512
    DEFAULT_COMPRESSION = 'deflate'
    DEFAULT_OVERVIEW_LEVELS = [2, 4, 8, 16, 32]
    
    def __init__(self, compression: str = 'deflate', block_size: int = 512):
        """
        Initialize GeoTIFF exporter.
        
        Args:
            compression: Compression codec ('deflate', 'lzw', 'zstd')
            block_size: Tile block size in pixels (default 512)
        """
        self.compression = compression
        self.block_size = block_size
        
    def write_dtm_cog(
        self,
        dtm_path: str,
        output_path: str,
        compression: Optional[str] = None,
        block_size: Optional[int] = None,
        overview_levels: Optional[list] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """
        Convert DTM to Cloud Optimized GeoTIFF.
        
        Args:
            dtm_path: Path to source GeoTIFF
            output_path: Path to output COG
            compression: Override default compression
            block_size: Override default block size
            overview_levels: Override default overview levels
            progress_callback: Progress callback(percent, message)
            
        Returns:
            Path to created COG file
        """
        compression = compression or self.compression
        block_size = block_size or self.block_size
        overview_levels = overview_levels or self.DEFAULT_OVERVIEW_LEVELS
        
        def _progress(pct, msg):
            logger.info(f"[{pct:3d}%] {msg}")
            if progress_callback:
                progress_callback(pct, msg)
        
        _progress(5, "Reading source DTM")
        
        try:
            with rasterio.open(dtm_path) as src:
                data = src.read(1)
                profile = src.profile.copy()
                
            _progress(15, "Creating tiled GeoTIFF with overviews")
            
            # Create temporary tiled file with overviews
            temp_fd, temp_tif = tempfile.mkstemp(suffix=".tif")
            os.close(temp_fd)
            
            try:
                # Write tiled profile
                tiled_profile = profile.copy()
                tiled_profile.update({
                    "driver": "GTiff",
                    "dtype": rasterio.float32,
                    "compress": compression,
                    "predictor": 2,
                    "tiled": True,
                    "blockxsize": block_size,
                    "blockysize": block_size,
                    "interleave": "band",
                })
                
                # Write data
                with rasterio.open(temp_tif, "w", **tiled_profile) as dst:
                    dst.write(data.astype(np.float32), 1)
                    
                _progress(40, "Building overview pyramid")
                
                # Build overviews
                with rasterio.open(temp_tif, "r+") as dst:
                    dst.build_overviews(overview_levels, Resampling.average)
                    dst.update_tags(ns="rio_overview", resampling="average")
                
                _progress(60, "Writing Cloud Optimized GeoTIFF")
                
                # Copy as COG (reorders data for cloud access)
                rio_copy(
                    temp_tif,
                    output_path,
                    driver="GTiff",
                    compress=compression,
                    predictor=2,
                    tiled=True,
                    blockxsize=block_size,
                    blockysize=block_size,
                    copy_src_overviews=True,
                )
                
                _progress(90, f"Validating COG format")
                self._validate_cog(output_path)
                
                _progress(100, "DTM COG export complete")
                
                file_size_mb = os.path.getsize(output_path) / 1e6
                logger.info(
                    f"DTM COG created: {output_path} ({file_size_mb:.1f} MB, "
                    f"compression={compression}, block={block_size}px)"
                )
                
                return output_path
                
            finally:
                if os.path.exists(temp_tif):
                    os.remove(temp_tif)
                    
        except Exception as e:
            logger.error(f"DTM COG export failed: {e}", exc_info=True)
            raise
    
    def write_drainage_raster_cog(
        self,
        raster_path: str,
        output_path: str,
        colormap: Optional[Dict[int, Tuple[int, int, int, int]]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """
        Convert drainage network raster to Cloud Optimized GeoTIFF.
        
        Args:
            raster_path: Path to drainage raster
            output_path: Path to output COG
            colormap: Optional color mapping for channels
            progress_callback: Progress callback
            
        Returns:
            Path to created COG
        """
        def _progress(pct, msg):
            logger.info(f"[{pct:3d}%] {msg}")
            if progress_callback:
                progress_callback(pct, msg)
        
        _progress(5, "Reading drainage raster")
        
        try:
            with rasterio.open(raster_path) as src:
                data = src.read(1)
                profile = src.profile.copy()
            
            _progress(35, "Creating Cloud Optimized GeoTIFF")
            
            tiled_profile = profile.copy()
            tiled_profile.update({
                "driver": "GTiff",
                "compress": "deflate",
                "predictor": 2,
                "tiled": True,
                "blockxsize": 512,
                "blockysize": 512,
            })
            
            # Create temporary file
            temp_fd, temp_tif = tempfile.mkstemp(suffix=".tif")
            os.close(temp_fd)
            
            try:
                with rasterio.open(temp_tif, "w", **tiled_profile) as dst:
                    dst.write(data, 1)
                    if colormap:
                        dst.write_colormap(1, colormap)
                        
                    # Build overviews
                    dst.build_overviews([2, 4, 8], Resampling.nearest)
                    dst.update_tags(ns="rio_overview", resampling="nearest")
                
                _progress(70, "Finalizing Cloud Optimized format")
                
                rio_copy(
                    temp_tif,
                    output_path,
                    driver="GTiff",
                    compress="deflate",
                    tiled=True,
                    blockxsize=512,
                    blockysize=512,
                    copy_src_overviews=True,
                )
                
                _progress(95, "Validating COG")
                self._validate_cog(output_path)
                
                _progress(100, "Drainage raster COG export complete")
                
                logger.info(f"Drainage raster COG created: {output_path}")
                return output_path
                
            finally:
                if os.path.exists(temp_tif):
                    os.remove(temp_tif)
                    
        except Exception as e:
            logger.error(f"Drainage raster COG export failed: {e}", exc_info=True)
            raise
    
    def _validate_cog(self, cog_path: str) -> bool:
        """
        Validate COG format.
        
        Returns:
            True if valid, False otherwise (logs warning but doesn't raise)
        """
        try:
            with rasterio.open(cog_path) as src:
                is_tiled = src.profile.get("tiled", False)
                has_overviews = bool(src.overviews(1))
                compress = src.profile.get("compress", "none")
                blocksize = src.profile.get("blockxsize", "?")
                
            if not is_tiled:
                logger.warning(f"COG validation: {cog_path} is NOT tiled")
                return False
            if not has_overviews:
                logger.warning(f"COG validation: {cog_path} has NO overviews")
                return False
                
            logger.info(
                f"COG validation successful - "
                f"compression={compress}, block={blocksize}px, overviews={src.overviews(1)}"
            )
            return True
            
        except Exception as e:
            logger.warning(f"COG validation could not complete: {e}")
            return False


class DrainageGeoJSONExporter:
    """
    Export drainage network as GeoJSON format.
    
    Supports:
    - LineString geometries for drainage channels
    - Point geometries for outlets
    - Feature properties (length, slope, flow, design type, etc.)
    - Valid GeoJSON RFC 7946 format
    """
    
    @staticmethod
    def export_drainage_network(
        drainage_lines: list,
        outlets: list,
        output_path: str,
        crs: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """
        Export drainage network to GeoJSON.
        
        Args:
            drainage_lines: List of (channel_type, coords_list, properties_dict)
            outlets: List of outlet dicts with x, y, z, edge properties
            output_path: Path to output GeoJSON
            crs: Coordinate reference system (e.g., 'EPSG:32644')
            progress_callback: Progress callback
            
        Returns:
            Path to created GeoJSON file
        """
        def _progress(pct, msg):
            logger.info(f"[{pct:3d}%] {msg}")
            if progress_callback:
                progress_callback(pct, msg)
        
        _progress(10, "Building GeoJSON feature collection")
        
        features = []
        
        # Drainage lines
        for channel_type, coords, props in drainage_lines:
            try:
                # Convert coordinates to (lon, lat, elevation) format for GeoJSON
                line_coords = [(c[0], c[1]) for c in coords]  # Extract x, y (lon, lat)
                
                # Create LineString geometry
                geometry = {
                    "type": "LineString",
                    "coordinates": line_coords
                }
                
                # Prepare properties with native Python types for JSON
                feature_props = {
                    "type": "drainage_line",
                    "channel_type": str(channel_type),
                }
                
                # Add all properties from props dict
                if props:
                    for key, val in props.items():
                        # Convert numpy types and other non-JSON-serializable types
                        if isinstance(val, (np.integer, np.floating)):
                            feature_props[key] = float(val) if isinstance(val, np.floating) else int(val)
                        elif isinstance(val, (list, tuple)):
                            feature_props[key] = [
                                float(v) if isinstance(v, (np.floating, float)) else 
                                (int(v) if isinstance(v, (np.integer, int)) else v)
                                for v in val
                            ]
                        elif isinstance(val, np.ndarray):
                            feature_props[key] = val.tolist()
                        elif val is None or isinstance(val, (str, int, float, bool)):
                            feature_props[key] = val
                        else:
                            feature_props[key] = str(val)
                
                features.append({
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": feature_props
                })
                
            except Exception as e:
                logger.warning(f"Could not export drainage line: {e}")
                continue
        
        _progress(50, "Adding outlet points")
        
        # Outlets
        for idx, outlet in enumerate(outlets):
            try:
                geometry = {
                    "type": "Point",
                    "coordinates": [float(outlet['x']), float(outlet['y'])]
                }
                
                feature_props = {
                    "type": "outlet",
                    "outlet_index": idx,
                    "edge": str(outlet.get('edge', 'unknown')),
                    "elevation_m": float(outlet.get('z', 0))
                }
                
                features.append({
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": feature_props
                })
                
            except Exception as e:
                logger.warning(f"Could not export outlet {idx}: {e}")
                continue
        
        _progress(75, "Writing GeoJSON file")
        
        # Create GeoJSON FeatureCollection
        geojson = {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {"name": crs or "EPSG:4326"}
            },
            "features": features,
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "total_lines": len(drainage_lines),
                "total_outlets": len(outlets),
                "generator": "Terra Pravah Export Service"
            }
        }
        
        # Write to file
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            _progress(100, "GeoJSON export complete")
            
            file_size_kb = os.path.getsize(output_path) / 1024
            logger.info(
                f"Drainage GeoJSON created: {output_path} "
                f"({file_size_kb:.1f} KB, {len(features)} features)"
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"GeoJSON export failed: {e}", exc_info=True)
            raise


class ExportManager:
    """
    High-level export manager for managing all export operations.
    
    Coordinates DTM export, drainage export, and report generation.
    """
    
    def __init__(self, output_dir: str):
        """
        Initialize export manager.
        
        Args:
            output_dir: Base directory for all exports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.geotiff_exporter = GeoTIFFExporter()
        
    def export_dtm(
        self,
        dtm_path: str,
        output_name: str = "dtm.cog.tif",
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """
        Export DTM as Cloud Optimized GeoTIFF.
        
        Args:
            dtm_path: Path to source DTM
            output_name: Output filename
            progress_callback: Progress callback
            
        Returns:
            Path to exported COG
        """
        output_path = str(self.output_dir / output_name)
        
        try:
            return self.geotiff_exporter.write_dtm_cog(
                dtm_path, output_path, progress_callback=progress_callback
            )
        except Exception as e:
            logger.error(f"DTM export failed: {e}")
            raise
    
    def export_drainage(
        self,
        drainage_lines: list,
        outlets: list,
        crs: Optional[str] = None,
        output_name: str = "drainage.geojson",
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """
        Export drainage network as GeoJSON.
        
        Args:
            drainage_lines: List of drainage channel data
            outlets: List of outlet points
            crs: Coordinate reference system
            output_name: Output filename
            progress_callback: Progress callback
            
        Returns:
            Path to exported GeoJSON
        """
        output_path = str(self.output_dir / output_name)
        
        try:
            return DrainageGeoJSONExporter.export_drainage_network(
                drainage_lines, outlets, output_path, crs, progress_callback
            )
        except Exception as e:
            logger.error(f"Drainage export failed: {e}")
            raise
