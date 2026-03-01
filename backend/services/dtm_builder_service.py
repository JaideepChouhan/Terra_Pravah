"""
dtm_builder_service.py
Orchestrates LAS/LAZ -> conditioned GeoTIFF pipeline for Terra Pravah.
"""

import os
import tempfile
from typing import Optional, Callable, Dict, Any

from .dtm_builder import build_dtm, condition_dtm, validate_dtm


class DTMBuilderService:
    """High-level service used by API layer for DTM generation."""

    def __init__(self, upload_folder: str, results_folder: str):
        self.upload_folder = upload_folder
        self.results_folder = results_folder
        os.makedirs(results_folder, exist_ok=True)

    def process_las(
        self,
        las_filename: str,
        resolution: float = 1.0,
        epsg: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Dict[str, Any]:
        """Build conditioned DTM from LAS/LAZ file in upload directory."""
        las_path = os.path.join(self.upload_folder, las_filename)
        if not os.path.exists(las_path):
            raise FileNotFoundError(f"LAS file not found: {las_path}")

        base = os.path.splitext(las_filename)[0]

        with tempfile.TemporaryDirectory() as tmpdir:
            raw_tif = os.path.join(tmpdir, f"{base}_raw.tif")
            conditioned_tif = os.path.join(self.results_folder, f"{base}_dtm.tif")

            def _relay_progress(pct: int, msg: str):
                if progress_callback:
                    progress_callback(int(pct * 0.80), msg)

            metadata = build_dtm(
                las_path=las_path,
                output_tif=raw_tif,
                resolution=resolution,
                epsg=epsg,
                progress_callback=_relay_progress,
            )

            if progress_callback:
                progress_callback(82, "Conditioning DTM (filling sinks) …")
            condition_dtm(raw_tif, conditioned_tif)

        if progress_callback:
            progress_callback(95, "Validating output …")
        validation = validate_dtm(conditioned_tif)

        if progress_callback:
            progress_callback(100, "DTM ready.")

        return {
            "dtm_path": conditioned_tif,
            "validation": validation,
            "metadata": metadata,
        }
