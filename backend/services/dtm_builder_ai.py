"""
dtm_builder_ai.py
=================
AI-powered DTM pipeline for Terra Pravah.
Fixes applied vs original version:

  FIX 1 — Temp-dir race condition
    Original: raw_tif was written inside `with TemporaryDirectory()`, which
    deleted the dir before condition_dtm() was called → FileNotFoundError.
    Fix: intermediate files go to results_folder/temp/. They are cleaned up
    in a try/finally block after conditioning completes successfully.

  FIX 2 — Filenames with spaces/parentheses
    WhiteboxTools and some GDAL drivers fail silently on paths that contain
    spaces or special characters. All intermediate paths now use a sanitized
    stem (spaces → underscores, special chars stripped).

  FIX 3 — Cloud Optimized GeoTIFF (COG) output
    The final conditioned DTM is written as a proper COG: tiled 512×512,
    DEFLATE compressed, predictor-2, with built-in overview pyramid
    (levels 2/4/8/16/32). The COG is validated via rasterio.

Part of Terra Pravah v2.3 — MoPR Hackathon Pipeline
"""

import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Callable, Dict, Any

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.shutil import copy as rio_copy

from dtm_builder import (
    read_las,
    downsample_points,
    IDWInterpolator,
    write_geotiff,
    condition_dtm,
    validate_dtm,
)
from ai_ground_classifier import AIGroundClassifier

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _safe_stem(filename: str) -> str:
    """
    Convert an arbitrary filename stem to one safe for all tools.

    '64334_2H (REFLIGHT)_POINT CLOUD.LAS'
    → '64334_2H_REFLIGHT_POINT_CLOUD'

    Rules:
      - Take the stem (no extension)
      - Replace runs of non-alphanumeric / non-dash chars with a single '_'
      - Strip leading/trailing underscores
      - Fall back to 'dtm' if nothing is left
    """
    stem = Path(filename).stem
    safe = re.sub(r'[^\w-]+', '_', stem).strip('_')
    return safe or "dtm"


def write_cog(input_tif: str, output_cog: str,
              overview_levels: list = None,
              compress: str = "deflate",
              block_size: int = 512) -> str:
    """
    Convert any GeoTIFF to a valid Cloud Optimized GeoTIFF (COG).

    A COG has three requirements:
      1. Tiled internally (blockxsize = blockysize = 512 by convention)
      2. Overview pyramid embedded in the file (levels 2, 4, 8, 16, 32)
      3. Data and overviews ordered so a range-request can read any zoom level
         without reading the whole file (achieved by copy_src_overviews=True)

    Strategy:
      a) Read input TIF into memory
      b) Write a tiled+overview TIF to a NamedTemporaryFile (same filesystem
         as output_cog so the final copy is a rename, not a cross-device copy)
      c) Call rasterio.shutil.copy with copy_src_overviews=True to produce
         the final COG in one pass — this is the only way to get the correct
         internal layout

    Args:
        input_tif:       Path to any valid GeoTIFF.
        output_cog:      Destination path for the COG (extension .cog.tif
                         recommended but not required).
        overview_levels: Downsample levels (default [2, 4, 8, 16, 32]).
        compress:        Compression codec ('deflate' or 'lzw').
        block_size:      Tile edge length in pixels (default 512).

    Returns:
        output_cog path.
    """
    if overview_levels is None:
        overview_levels = [2, 4, 8, 16, 32]

    os.makedirs(os.path.dirname(os.path.abspath(output_cog)), exist_ok=True)

    # ── Step a: read source ───────────────────────────────────────────────────
    with rasterio.open(input_tif) as src:
        data    = src.read(1)
        profile = src.profile.copy()

    # ── Step b: write tiled + overview intermediate ───────────────────────────
    # Use same parent dir as output_cog so rename stays on the same filesystem
    out_dir = os.path.dirname(os.path.abspath(output_cog))
    tmp_fd, tmp_ovr = tempfile.mkstemp(suffix="_ovr.tif", dir=out_dir)
    os.close(tmp_fd)

    try:
        tiled_profile = profile.copy()
        tiled_profile.update({
            "driver":    "GTiff",
            "dtype":     rasterio.float32,
            "compress":  compress,
            "predictor": 2,        # horizontal differencing — works well for DEMs
            "tiled":     True,
            "blockxsize": block_size,
            "blockysize": block_size,
            "interleave": "band",
        })

        with rasterio.open(tmp_ovr, "w", **tiled_profile) as dst:
            dst.write(data.astype(np.float32), 1)

        # Build overviews into the tiled file (required before copy_src_overviews)
        with rasterio.open(tmp_ovr, "r+") as dst:
            dst.build_overviews(overview_levels, Resampling.average)
            dst.update_tags(ns="rio_overview", resampling="average")

        # ── Step c: copy as COG ───────────────────────────────────────────────
        # copy_src_overviews=True tells GDAL to write overviews before the main
        # image data, which is the defining characteristic of a COG.
        rio_copy(
            tmp_ovr,
            output_cog,
            driver      = "GTiff",
            compress    = compress,
            predictor   = 2,
            tiled       = True,
            blockxsize  = block_size,
            blockysize  = block_size,
            copy_src_overviews = True,
        )

    finally:
        if os.path.exists(tmp_ovr):
            os.remove(tmp_ovr)

    # ── Validate ──────────────────────────────────────────────────────────────
    _validate_cog(output_cog)

    size_mb = os.path.getsize(output_cog) / 1e6
    logger.info(f"  COG written: {output_cog}  ({size_mb:.1f} MB, "
                f"overviews={overview_levels}, compress={compress})")
    return output_cog


def _validate_cog(cog_path: str) -> None:
    """
    Lightweight COG validation: confirm tiling and overview presence.
    Logs a warning if either check fails — does not raise.
    """
    try:
        with rasterio.open(cog_path) as src:
            is_tiled    = src.profile.get("tiled", False)
            has_ovr     = bool(src.overviews(1))
            driver      = src.profile.get("driver", "?")
            compress    = src.profile.get("compress", "none")
            block_shape = src.profile.get("blockxsize", "?")

        if not is_tiled:
            logger.warning(f"  COG validation: {cog_path} is NOT tiled.")
        if not has_ovr:
            logger.warning(f"  COG validation: {cog_path} has NO overviews.")
        if is_tiled and has_ovr:
            logger.info(
                f"  COG validation OK — driver={driver}, "
                f"compress={compress}, block={block_shape}px, "
                f"overviews={src.overviews(1)}"
            )
    except Exception as e:
        logger.warning(f"  COG validation could not run: {e}")


# ─────────────────────────────────────────────────────────────────────────────
#  Standalone build function
# ─────────────────────────────────────────────────────────────────────────────

def build_dtm_ai(
    las_path:        str,
    output_tif:      str,
    model_path:      str,
    threshold_json:  Optional[str]                           = None,
    resolution:      float                                   = 1.0,
    epsg:            Optional[str]                           = None,
    max_points:      int                                     = 12,
    search_radius:   Optional[float]                         = None,
    downsample:      bool                                    = True,
    target_density:  float                                   = 10.0,
    chunk_size:      int                                     = 4096,
    device:          Optional[str]                           = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> dict:
    """
    Full AI-powered pipeline: LAS → AI ground filter → IDW → GeoTIFF.

    Note: this function writes a plain (non-COG) GeoTIFF.  The COG
    conversion is handled by DTMBuilderServiceAI.process_las() after
    hydrological conditioning.  This keeps the functions single-purpose.

    Args:
        las_path:       Path to input .las/.laz file.
        output_tif:     Destination path for the raw DTM GeoTIFF.
        model_path:     Path to best_model.pth or swa_model.pth.
        threshold_json: Path to threshold.json from training Cell 9 (optional).
        resolution:     Grid cell size in metres (default 1.0).
        epsg:           EPSG string e.g. 'EPSG:32644'. Uses LAS header if None.
        max_points:     IDW nearest neighbours.
        search_radius:  IDW search radius in metres (default: 5 × resolution).
        downsample:     Thin the point cloud before inference (recommended).
        target_density: Target points/m² after downsampling.
        chunk_size:     Points per model forward pass (default 4096).
        device:         'cpu' or 'cuda'. Auto-detected if None.
        progress_callback: Optional callable(pct: int, message: str).

    Returns:
        dict with metadata: bounds, point counts, ai_classification, etc.
    """
    def _progress(pct, msg):
        logger.info(f"[{pct:3d}%] {msg}")
        if progress_callback:
            progress_callback(pct, msg)

    _progress(0, "Starting AI DTM build pipeline …")

    # ── Step 1: Read LAS ──────────────────────────────────────────────────────
    _progress(5, "Reading LAS file …")
    points, header, pre_filtered = read_las(las_path)
    total_points = len(points)

    crs = epsg
    if crs is None:
        try:
            wkt = header.parse_crs()
            epsg_code = wkt.to_epsg()
            if epsg_code:
                crs = f"EPSG:{epsg_code}"
                logger.info(f"  CRS from LAS header: {crs}")
        except Exception:
            logger.warning("  CRS not found in LAS header.")

    # ── Step 2: Downsample ────────────────────────────────────────────────────
    if downsample and not pre_filtered:
        _progress(15, "Downsampling point cloud …")
        points = downsample_points(
            points, target_density=target_density, method="grid")

    # ── Step 3: AI Ground Classification ─────────────────────────────────────
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
        ground_points = points
        ai_stats = {"note": "Used pre-classified ground points from LAS"}
        _progress(30, "Using pre-classified ground points from LAS.")

    if len(ground_points) == 0:
        raise RuntimeError(
            "AI classifier returned zero ground points. "
            "Try a lower threshold (e.g. threshold=0.35)."
        )

    # ── Step 4: Bounds ────────────────────────────────────────────────────────
    bounds = (
        float(ground_points[:, 0].min()), float(ground_points[:, 0].max()),
        float(ground_points[:, 1].min()), float(ground_points[:, 1].max()),
    )

    # ── Step 5: IDW Interpolation ─────────────────────────────────────────────
    _progress(50, "Interpolating DTM (IDW) …")
    interpolator = IDWInterpolator(
        resolution=resolution,
        max_points=max_points,
        search_radius=search_radius or resolution * 5,
    )
    x, y, grid = interpolator.interpolate(ground_points, bounds)

    # ── Step 6: Write raw GeoTIFF ─────────────────────────────────────────────
    _progress(85, "Writing raw GeoTIFF …")
    write_geotiff(output_tif, grid, x, y, crs=crs)

    _progress(100, f"AI DTM build complete → {output_tif}")

    return {
        "output_tif":         output_tif,
        "crs":                crs,
        "bounds":             bounds,
        "resolution_m":       resolution,
        "total_input_points": total_points,
        "ground_points":      len(ground_points),
        "grid_shape":         grid.shape,
        "pre_filtered":       pre_filtered,
        "ai_classification":  ai_stats,
        "model_path":         model_path,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  High-level service
# ─────────────────────────────────────────────────────────────────────────────

class DTMBuilderServiceAI:
    """
    Drop-in replacement for DTMBuilderService.

    Changes vs DTMBuilderService:
      • Adds model_path and threshold_json for AI ground classification.
      • Writes final output as Cloud Optimized GeoTIFF (.cog.tif).
      • Uses results_folder/temp/ for intermediates (no TemporaryDirectory).
      • Sanitizes filenames — safe for WhiteboxTools and all GDAL drivers.

    Example
    -------
    service = DTMBuilderServiceAI(
        upload_folder   = "uploads",
        results_folder  = "results",
        model_path      = "backend/models/dtm_outputs_finetuned/best_model.pth",
        threshold_json  = "backend/models/dtm_outputs_finetuned/threshold.json",
    )
    result = service.process_las("my_village.las", resolution=1.0)
    print(result["dtm_path"])   # → results/my_village.cog.tif
    """

    def __init__(
        self,
        upload_folder:   str,
        results_folder:  str,
        model_path:      str,
        threshold_json:  Optional[str] = None,
        chunk_size:      int           = 4096,
        device:          Optional[str] = None,
    ):
        self.upload_folder  = upload_folder
        self.results_folder = results_folder
        self.model_path     = model_path
        self.threshold_json = threshold_json
        self.chunk_size     = chunk_size
        self.device         = device

        os.makedirs(results_folder, exist_ok=True)

        # Fail fast — don't wait until process_las() is called
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                "Place best_model.pth in the models directory."
            )

        logger.info(
            f"DTMBuilderServiceAI initialised:\n"
            f"  model_path     = {model_path}\n"
            f"  upload_folder  = {upload_folder}\n"
            f"  results_folder = {results_folder}"
        )

    def process_las(
        self,
        las_filename:     str,
        resolution:       float                                   = 1.0,
        epsg:             Optional[str]                           = None,
        progress_callback: Optional[Callable[[int, str], None]]  = None,
    ) -> Dict[str, Any]:
        """
        Build a hydrologically conditioned Cloud Optimized GeoTIFF from a
        LAS/LAZ file.

        File lifecycle (all intermediate files use the sanitized stem):
          uploads/<original filename>.las            ← input (unchanged)
          results/temp/<safe_stem>_raw.tif           ← raw IDW output
          results/temp/<safe_stem>_conditioned.tif   ← after sink-filling
          results/<safe_stem>.cog.tif                ← FINAL COG output

        The temp/ subdirectory is cleaned up after successful COG creation.
        On failure the temp files are left in place for debugging.

        Returns:
            dict with keys: dtm_path, validation, metadata, ai_classification.
        """
        las_path = os.path.join(self.upload_folder, las_filename)
        if not os.path.exists(las_path):
            raise FileNotFoundError(f"LAS file not found: {las_path}")

        # ── Sanitize stem — safe for WhiteboxTools and GDAL ──────────────────
        safe_stem = _safe_stem(las_filename)
        logger.info(f"  Safe stem: '{safe_stem}' (original: '{las_filename}')")

        # ── Persistent intermediate directory (not a TemporaryDirectory) ──────
        temp_dir = os.path.join(self.results_folder, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        raw_tif         = os.path.join(temp_dir, f"{safe_stem}_raw.tif")
        conditioned_tif = os.path.join(temp_dir, f"{safe_stem}_conditioned.tif")
        final_cog       = os.path.join(self.results_folder, f"{safe_stem}.cog.tif")

        def _relay(pct: int, msg: str) -> None:
            if progress_callback:
                progress_callback(int(pct * 0.75), msg)   # 0–75% for AI+IDW

        try:
            # ── Stage 1: AI ground classification + IDW ───────────────────────
            metadata = build_dtm_ai(
                las_path        = las_path,
                output_tif      = raw_tif,
                model_path      = self.model_path,
                threshold_json  = self.threshold_json,
                resolution      = resolution,
                epsg            = epsg,
                chunk_size      = self.chunk_size,
                device          = self.device,
                progress_callback = _relay,
            )

            # ── Stage 2: Hydrological conditioning ───────────────────────────
            if progress_callback:
                progress_callback(78, "Conditioning DTM (filling sinks) …")
            logger.info(f"  Conditioning: {raw_tif} → {conditioned_tif}")
            condition_dtm(raw_tif, conditioned_tif)

            # ── Stage 3: Convert to Cloud Optimized GeoTIFF ──────────────────
            if progress_callback:
                progress_callback(88, "Converting to Cloud Optimized GeoTIFF …")
            logger.info(f"  Writing COG: {final_cog}")
            write_cog(conditioned_tif, final_cog)

            # ── Stage 4: Validate final output ────────────────────────────────
            if progress_callback:
                progress_callback(96, "Validating COG …")
            validation = validate_dtm(final_cog)

            if progress_callback:
                progress_callback(100, "AI DTM ready.")

            # ── Stage 5: Clean up temp files (only on success) ────────────────
            _cleanup_temp(raw_tif, conditioned_tif)

        except Exception:
            logger.error(
                "Pipeline failed. Intermediate files preserved for debugging:\n"
                f"  raw_tif:         {raw_tif}\n"
                f"  conditioned_tif: {conditioned_tif}"
            )
            raise

        return {
            "dtm_path":          final_cog,
            "validation":        validation,
            "metadata":          metadata,
            "ai_classification": metadata.get("ai_classification", {}),
        }


def _cleanup_temp(*paths: str) -> None:
    """Remove intermediate files; log but do not raise on failure."""
    for p in paths:
        try:
            if os.path.exists(p):
                os.remove(p)
                logger.debug(f"  Removed temp file: {p}")
        except OSError as e:
            logger.warning(f"  Could not remove temp file {p}: {e}")

    # Remove temp dir if empty
    for p in paths:
        d = os.path.dirname(p)
        try:
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
                logger.debug(f"  Removed empty temp dir: {d}")
        except OSError:
            pass