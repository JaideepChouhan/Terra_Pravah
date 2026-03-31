"""
dtm_builder_ai.py
=================
Modified version of dtm_builder_service.py that uses the AI ground classifier
(DTMPointNet2) instead of the PMF filter.

Only ONE function call changes compared to the original pipeline:
  GroundPointExtractor().extract(points)
  →  AIGroundClassifier(model_path).extract(points)

Everything else — IDW interpolation, GeoTIFF export, hydrological conditioning —
stays exactly the same.

How to use:
  Replace your import of DTMBuilderService with DTMBuilderServiceAI, or
  call build_dtm_ai() directly.

Part of Terra Pravah v2.3 — MoPR Hackathon Pipeline (AI Integration)
"""

import os
import logging
import tempfile
from typing import Optional, Callable, Dict, Any

# ── Existing pipeline components (unchanged) ──────────────────────────────────
from dtm_builder import (
    read_las,
    downsample_points,
    IDWInterpolator,
    write_geotiff,
    condition_dtm,
    validate_dtm,
)

# ── New AI classifier ─────────────────────────────────────────────────────────
from ai_ground_classifier import AIGroundClassifier

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Standalone build function (lowest-level entry point)
# ─────────────────────────────────────────────────────────────────────────────

def build_dtm_ai(
    las_path: str,
    output_tif: str,
    model_path: str,
    threshold_json: Optional[str] = None,
    resolution: float = 1.0,
    epsg: Optional[str] = None,
    max_points: int = 12,
    search_radius: Optional[float] = None,
    downsample: bool = True,
    target_density: float = 10.0,
    chunk_size: int = 4096,
    device: Optional[str] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> dict:
    """
    AI-powered version of build_dtm():
      LAS → AI ground filter → IDW interpolation → GeoTIFF

    Args:
        las_path:       Path to input .las file.
        output_tif:     Path for the output raw DTM GeoTIFF.
        model_path:     Path to best_model.pth or swa_model.pth.
        threshold_json: Path to threshold.json from training Cell 9 (optional
                        but recommended — picks optimal threshold automatically).
        resolution:     Grid cell size in metres (default 1.0).
        epsg:           EPSG string, e.g. 'EPSG:32644'.
        max_points:     IDW nearest neighbours.
        search_radius:  IDW search radius in metres.
        downsample:     Whether to thin before AI inference.
        target_density: Target points/m² after downsampling.
        chunk_size:     Points per model forward pass (default 4096).
        device:         'cpu' or 'cuda'. Auto-detected if None.
        progress_callback: Optional callable(pct: int, message: str).

    Returns:
        dict with metadata including ground_point_count, output_tif, etc.
    """

    def _progress(pct, msg):
        logger.info(f"[{pct:3d}%] {msg}")
        if progress_callback:
            progress_callback(pct, msg)

    _progress(0, "Starting AI DTM build pipeline …")

    # ── Step 1: Read LAS ─────────────────────────────────────────────────────
    _progress(5, "Reading LAS file …")
    points, header, pre_filtered = read_las(las_path)
    total_points = len(points)

    # Determine CRS
    crs = epsg
    if crs is None:
        try:
            wkt = header.parse_crs()
            crs = wkt.to_epsg()
            if crs:
                crs = f"EPSG:{crs}"
                logger.info(f"  CRS from LAS header: {crs}")
        except Exception:
            logger.warning("  CRS not found in LAS header.")

    # ── Step 2: Optional downsampling ────────────────────────────────────────
    if downsample and not pre_filtered:
        _progress(15, "Downsampling point cloud …")
        points = downsample_points(points, target_density=target_density, method="grid")

    # ── Step 3: AI Ground Classification (replaces PMF) ──────────────────────
    if not pre_filtered:
        _progress(25, "Loading AI ground classifier …")
        clf = AIGroundClassifier(
            model_path=model_path,
            threshold_json=threshold_json,
            chunk_size=chunk_size,
            device=device,
        )

        _progress(30, "Running AI ground classification …")
        ground_points, ai_stats = clf.extract_with_stats(points)
        logger.info(
            f"  AI stats: {ai_stats['ground_points']:,} ground "
            f"({ai_stats['ground_pct']}%) threshold={ai_stats['threshold']}"
        )
    else:
        # LAS already has ground classification (class 2) — skip AI
        ground_points = points
        ai_stats = {"note": "Used pre-classified ground points from LAS"}
        _progress(30, "Using pre-classified ground points from LAS.")

    if len(ground_points) == 0:
        raise RuntimeError(
            "AI classifier returned zero ground points. "
            "Try a lower threshold (e.g. 0.3) or check the model file."
        )

    # ── Step 4: Compute bounds ────────────────────────────────────────────────
    xmin = float(ground_points[:, 0].min())
    xmax = float(ground_points[:, 0].max())
    ymin = float(ground_points[:, 1].min())
    ymax = float(ground_points[:, 1].max())
    bounds = (xmin, xmax, ymin, ymax)

    # ── Step 5: IDW Interpolation ────────────────────────────────────────────
    _progress(50, "Interpolating DTM (IDW) …")
    interpolator = IDWInterpolator(
        resolution=resolution,
        max_points=max_points,
        search_radius=search_radius or resolution * 5,
    )
    x, y, grid = interpolator.interpolate(ground_points, bounds)

    # ── Step 6: Write GeoTIFF ────────────────────────────────────────────────
    _progress(85, "Writing GeoTIFF …")
    write_geotiff(output_tif, grid, x, y, crs=crs)

    _progress(100, f"AI DTM build complete → {output_tif}")

    return {
        "output_tif":          output_tif,
        "crs":                 crs,
        "bounds":              bounds,
        "resolution_m":        resolution,
        "total_input_points":  total_points,
        "ground_points":       len(ground_points),
        "grid_shape":          grid.shape,
        "pre_filtered":        pre_filtered,
        "ai_classification":   ai_stats,
        "model_path":          model_path,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  High-level service (mirrors DTMBuilderService from dtm_builder_service.py)
# ─────────────────────────────────────────────────────────────────────────────

class DTMBuilderServiceAI:
    """
    Drop-in replacement for DTMBuilderService.
    Adds model_path and threshold_json parameters; everything else is the same.

    Example
    -------
    service = DTMBuilderServiceAI(
        upload_folder="uploads",
        results_folder="results",
        model_path="models/best_model.pth",
        threshold_json="models/threshold.json",
    )
    result = service.process_las("my_village.las", resolution=1.0)
    print(result["dtm_path"])
    """

    def __init__(
        self,
        upload_folder: str,
        results_folder: str,
        model_path: str,
        threshold_json: Optional[str] = None,
        chunk_size: int = 4096,
        device: Optional[str] = None,
    ):
        self.upload_folder  = upload_folder
        self.results_folder = results_folder
        self.model_path     = model_path
        self.threshold_json = threshold_json
        self.chunk_size     = chunk_size
        self.device         = device
        os.makedirs(results_folder, exist_ok=True)

        # Validate model file exists at startup (fail fast)
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                "Extract best_model.pth from your zip file and update model_path."
            )

        logger.info(f"DTMBuilderServiceAI initialised: model={model_path}")

    def process_las(
        self,
        las_filename: str,
        resolution: float = 1.0,
        epsg: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Build a conditioned DTM from a LAS/LAZ file using the AI classifier.
        Mirrors DTMBuilderService.process_las() exactly.

        Returns:
            dict with keys: dtm_path, validation, metadata, ai_classification.
        """
        las_path = os.path.join(self.upload_folder, las_filename)
        if not os.path.exists(las_path):
            raise FileNotFoundError(f"LAS file not found: {las_path}")

        base = os.path.splitext(las_filename)[0]

        with tempfile.TemporaryDirectory() as tmpdir:
            raw_tif        = os.path.join(tmpdir, f"{base}_raw.tif")
            conditioned_tif = os.path.join(self.results_folder, f"{base}_dtm_ai.tif")

            def _relay(pct, msg):
                if progress_callback:
                    progress_callback(int(pct * 0.80), msg)

            metadata = build_dtm_ai(
                las_path=las_path,
                output_tif=raw_tif,
                model_path=self.model_path,
                threshold_json=self.threshold_json,
                resolution=resolution,
                epsg=epsg,
                chunk_size=self.chunk_size,
                device=self.device,
                progress_callback=_relay,
            )

        if progress_callback:
            progress_callback(82, "Conditioning DTM (filling sinks) …")
        condition_dtm(raw_tif, conditioned_tif)

        if progress_callback:
            progress_callback(95, "Validating output …")
        validation = validate_dtm(conditioned_tif)

        if progress_callback:
            progress_callback(100, "AI DTM ready.")

        return {
            "dtm_path":          conditioned_tif,
            "validation":        validation,
            "metadata":          metadata,
            "ai_classification": metadata.get("ai_classification", {}),
        }
