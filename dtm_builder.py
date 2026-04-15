"""
dtm_builder.py
==============
AI-Driven Digital Terrain Model (DTM) Builder for Terra Pravah
Converts raw .las point cloud files into hydrologically conditioned GeoTIFF DTMs.

Pipeline:
  1. Read .las file (memory-efficient)
  2. Ground point segmentation using Progressive Morphological Filter (PMF)
  3. DTM interpolation using Inverse Distance Weighting (IDW) with adaptive power
  4. Hydrological conditioning (sink filling via WhiteboxTools)
  5. Export as GeoTIFF

Author: Terra Pravah Team
"""

import os
import logging
import numpy as np
import laspy
import rasterio
from rasterio.transform import from_origin
from scipy.spatial import cKDTree

# Optional imports (used with fallbacks)
try:
    import whitebox
    WHITEBOX_AVAILABLE = True
except ImportError:
    WHITEBOX_AVAILABLE = False

try:
    from scipy.ndimage import generic_filter
    SCIPY_NDIMAGE_AVAILABLE = True
except ImportError:
    SCIPY_NDIMAGE_AVAILABLE = False

# ─────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  1. LAS File Reader
# ─────────────────────────────────────────────

def read_las(las_path: str, use_existing_classification: bool = True):
    """
    Read a .las/.laz point cloud file and return points as a NumPy array.

    Args:
        las_path: Path to the .las file.
        use_existing_classification: If True and the file has ground
            classification (class 2), return only those points as pre-filtered.

    Returns:
        points (np.ndarray): Shape (N, 3) — columns are X, Y, Z.
        header (laspy.LasHeader): File header with CRS/scale/offset metadata.
        pre_filtered (bool): True if existing ground classification was used.
    """
    if not os.path.exists(las_path):
        raise FileNotFoundError(f"LAS file not found: {las_path}")

    logger.info(f"Reading LAS file: {las_path}")
    las = laspy.read(las_path)

    x = np.array(las.x, dtype=np.float64)
    y = np.array(las.y, dtype=np.float64)
    z = np.array(las.z, dtype=np.float64)
    points = np.column_stack([x, y, z])

    logger.info(f"  Total points loaded: {len(points):,}")

    # Use existing ground classification if available (LAS class 2 = ground)
    pre_filtered = False
    if use_existing_classification:
        try:
            classifications = np.array(las.classification)
            ground_mask = classifications == 2
            n_ground = ground_mask.sum()
            if n_ground > 1000:
                logger.info(f"  Using existing classification: {n_ground:,} ground points (class 2)")
                points = points[ground_mask]
                pre_filtered = True
        except AttributeError:
            logger.info("  No classification data found; will apply PMF filter.")

    return points, las.header, pre_filtered


def downsample_points(points: np.ndarray, target_density: float = 5.0,
                      method: str = "grid") -> np.ndarray:
    """
    Reduce point density for faster processing.

    Args:
        points: (N, 3) array of XYZ points.
        target_density: Target points per m² (default 5).
        method: 'grid' keeps the lowest point per cell (best for PMF),
                'random' does random sampling.

    Returns:
        Downsampled points array.
    """
    if method == "random":
        area = ((points[:, 0].max() - points[:, 0].min()) *
                (points[:, 1].max() - points[:, 1].min()))
        target_n = int(area * target_density)
        if target_n >= len(points):
            return points
        idx = np.random.choice(len(points), target_n, replace=False)
        logger.info(f"  Random downsampled: {len(points):,} → {len(idx):,} points")
        return points[idx]

    # Grid method: keep minimum-Z point per cell (preserves ground shape)
    cell_size = 1.0 / np.sqrt(target_density)
    xmin, ymin = points[:, 0].min(), points[:, 1].min()
    ix = np.floor((points[:, 0] - xmin) / cell_size).astype(np.int32)
    iy = np.floor((points[:, 1] - ymin) / cell_size).astype(np.int32)
    nx = int((points[:, 0].max() - xmin) / cell_size) + 1
    cell_id = ix * nx + iy

    # Sort by cell_id then Z; keep first (lowest Z) per cell
    order = np.lexsort((points[:, 2], cell_id))
    sorted_cells = cell_id[order]
    _, first_idx = np.unique(sorted_cells, return_index=True)
    kept = order[first_idx]

    logger.info(f"  Grid downsampled: {len(points):,} → {len(kept):,} points")
    return points[kept]


# ─────────────────────────────────────────────
#  2. Ground Point Segmentation (PMF)
# ─────────────────────────────────────────────

def _compute_local_minima(points: np.ndarray, cell_size: float) -> np.ndarray:
    """
    Compute the minimum Z value within the grid cell of each point.
    Uses a fast numpy sort + reduceat approach (no pandas dependency).

    Returns:
        local_min (np.ndarray): Shape (N,), minimum Z for each point's cell.
    """
    xmin = points[:, 0].min()
    ymin = points[:, 1].min()

    ix = np.floor((points[:, 0] - xmin) / cell_size).astype(np.int32)
    iy = np.floor((points[:, 1] - ymin) / cell_size).astype(np.int32)
    nx = int((points[:, 0].max() - xmin) / cell_size) + 2
    cell_id = ix * nx + iy

    # Sort everything by cell_id
    order = np.argsort(cell_id, kind="stable")
    cell_id_sorted = cell_id[order]
    z_sorted = points[order, 2]

    # Find group boundaries
    change_idx = np.where(np.diff(cell_id_sorted) != 0)[0] + 1
    split = np.concatenate([[0], change_idx, [len(cell_id_sorted)]])

    # Build cell_id → min_z lookup using np.minimum.reduceat
    min_vals = np.minimum.reduceat(z_sorted, split[:-1])
    unique_cells = cell_id_sorted[split[:-1]]

    # Map every cell_id to its min value
    cell_min_map = dict(zip(unique_cells, min_vals))
    local_min_sorted = np.array([cell_min_map[c] for c in cell_id_sorted])

    # Restore original point order
    local_min = np.empty(len(points), dtype=np.float64)
    local_min[order] = local_min_sorted
    return local_min


def _compute_local_roughness(points: np.ndarray, radius: float = 5.0,
                              sample_size: int = 50_000) -> np.ndarray:
    """
    Estimate local terrain roughness (std dev of Z within radius) for each point.
    Uses a KDTree with optional subsampling for large clouds.
    """
    if len(points) > sample_size:
        idx = np.random.choice(len(points), sample_size, replace=False)
        sample = points[idx]
    else:
        sample = points

    tree = cKDTree(sample[:, :2])
    roughness = np.zeros(len(points), dtype=np.float32)

    # Process in batches to avoid memory explosion
    batch = 10_000
    for start in range(0, len(points), batch):
        end = min(start + batch, len(points))
        neighbors_list = tree.query_ball_point(points[start:end, :2], r=radius)
        for i, nbrs in enumerate(neighbors_list):
            if len(nbrs) >= 3:
                roughness[start + i] = float(np.std(sample[nbrs, 2]))

    return roughness


class GroundPointExtractor:
    """
    Progressive Morphological Filter (PMF) for ground point extraction.

    The algorithm runs at multiple window sizes. At each window size every
    point is compared to its grid-cell minimum; points within the adaptive
    threshold are marked as ground candidates.  Results are combined
    depending on overall terrain roughness.
    """

    def __init__(self,
                 cell_sizes: list = None,
                 base_slope: float = 0.5,
                 constant: float = 0.2,
                 flat_threshold: float = 0.5,
                 rough_threshold: float = 2.0):
        """
        Args:
            cell_sizes: Window sizes in metres for the PMF (default [1,2,4,8]).
            base_slope: Slope parameter controlling how threshold grows with window.
            constant: Minimum baseline threshold (metres).
            flat_threshold: Roughness std-dev below which terrain is "flat".
            rough_threshold: Roughness std-dev above which terrain is "very rough".
        """
        self.cell_sizes = cell_sizes or [1, 2, 4, 8]
        self.base_slope = base_slope
        self.constant = constant
        self.flat_threshold = flat_threshold
        self.rough_threshold = rough_threshold

    def extract(self, points: np.ndarray) -> np.ndarray:
        """
        Run the PMF and return only ground points.

        Args:
            points: (N, 3) XYZ array.

        Returns:
            ground_points: (M, 3) array where M ≤ N.
        """
        if len(points) == 0:
            raise ValueError("No points provided for ground extraction.")

        overall_roughness = float(np.std(points[:, 2]))
        logger.info(f"  Overall terrain roughness (Z std): {overall_roughness:.3f} m")

        ground_masks = []
        for w in self.cell_sizes:
            local_min = _compute_local_minima(points, w)
            thresh = self.base_slope * w + self.constant
            mask = (points[:, 2] - local_min) <= thresh
            ground_masks.append(mask)
            pct = mask.sum() / len(points) * 100
            logger.info(f"  Window {w:2d}m → threshold {thresh:.2f}m → "
                        f"{mask.sum():,} candidates ({pct:.1f}%)")

        ground_masks = np.array(ground_masks)

        # Flat: strict (intersection); moderate: weighted vote; rough: union
        if overall_roughness < self.flat_threshold:
            logger.info("  Terrain type: FLAT — using intersection of all window masks")
            final_mask = np.all(ground_masks, axis=0)
        elif overall_roughness > self.rough_threshold:
            logger.info("  Terrain type: ROUGH — using union of all window masks")
            final_mask = np.any(ground_masks, axis=0)
        else:
            # Vote: point is ground if it passes more than half the windows
            vote_count = ground_masks.sum(axis=0)
            threshold_votes = len(self.cell_sizes) // 2
            final_mask = vote_count > threshold_votes
            logger.info(f"  Terrain type: MODERATE — majority vote "
                        f"(>{threshold_votes} windows)")

        ground_points = points[final_mask]
        logger.info(f"  Ground points: {len(ground_points):,} / {len(points):,} "
                    f"({len(ground_points)/len(points)*100:.1f}%)")

        if len(ground_points) < 100:
            logger.warning("Very few ground points extracted! "
                           "Consider adjusting base_slope or constant.")

        return ground_points


# ─────────────────────────────────────────────
#  3. DTM Interpolation (IDW with adaptive power)
# ─────────────────────────────────────────────

def adaptive_power(density: float, roughness: float) -> float:
    """
    Compute adaptive IDW exponent based on local point density and roughness.

    Higher density → slightly higher power (sharper local influence).
    Higher roughness → lower power (smoother, spread influence).

    Args:
        density: Points per m².
        roughness: Local Z standard deviation (metres).

    Returns:
        IDW power (float), clamped to [1.0, 4.0].
    """
    base = 2.0
    density_factor = float(np.clip(density / 1000.0, 0.1, 0.3))
    roughness_factor = float(np.clip(roughness * 10.0, -0.5, 0.5))
    p = base + density_factor - roughness_factor
    return float(np.clip(p, 1.0, 4.0))


class IDWInterpolator:
    """
    Inverse Distance Weighting interpolator with adaptive power.

    For each grid cell the k nearest ground points within search_radius are
    found via a cKDTree. Their elevations are combined using IDW weights
    computed with an exponent that adapts to local density and roughness.
    """

    def __init__(self,
                 resolution: float = 1.0,
                 max_points: int = 12,
                 search_radius: float = None):
        """
        Args:
            resolution: Grid cell size in metres.
            max_points: Maximum nearest neighbours to use per cell.
            search_radius: Search radius in metres (default: 5 × resolution).
        """
        self.resolution = resolution
        self.max_points = max_points
        self.search_radius = search_radius or resolution * 5

    def interpolate(self, ground_points: np.ndarray,
                    bounds: tuple) -> tuple:
        """
        Interpolate ground points onto a regular grid.

        Args:
            ground_points: (N, 3) XYZ array of ground points.
            bounds: (xmin, xmax, ymin, ymax) in the same CRS.

        Returns:
            x (np.ndarray): 1-D array of column centre coordinates.
            y (np.ndarray): 1-D array of row centre coordinates.
            grid (np.ndarray): 2-D elevation grid, shape (len(y), len(x)).
                               NaN where no data.
        """
        xmin, xmax, ymin, ymax = bounds
        x = np.arange(xmin, xmax, self.resolution)
        y = np.arange(ymin, ymax, self.resolution)
        nx, ny = len(x), len(y)
        grid = np.full((ny, nx), np.nan, dtype=np.float32)

        logger.info(f"  Building KDTree for {len(ground_points):,} ground points …")
        tree = cKDTree(ground_points[:, :2])

        logger.info(f"  Interpolating {ny}×{nx} = {ny*nx:,} cells "
                    f"(resolution={self.resolution}m) …")

        # Build full grid of query coordinates for vectorised tree query
        gx, gy = np.meshgrid(x, y)                        # (ny, nx)
        query_pts = np.column_stack([gx.ravel(), gy.ravel()])  # (ny*nx, 2)

        # Query k nearest within radius
        dists, idxs = tree.query(
            query_pts,
            k=min(self.max_points, len(ground_points)),
            distance_upper_bound=self.search_radius,
            workers=-1          # use all CPU cores (scipy ≥ 1.9)
        )

        # Handle case where tree.query returns 1-D for k=1
        if dists.ndim == 1:
            dists = dists[:, np.newaxis]
            idxs = idxs[:, np.newaxis]

        total_cells = ny * nx
        for flat_i in range(total_cells):
            d = dists[flat_i]
            idx = idxs[flat_i]
            valid = d < np.inf
            if not np.any(valid):
                continue

            d_v = d[valid]
            z_v = ground_points[idx[valid], 2]

            # Adaptive power
            local_density = valid.sum() / (np.pi * self.search_radius ** 2 + 1e-9)
            local_roughness = float(np.std(z_v)) if len(z_v) > 1 else 0.0
            p = adaptive_power(local_density, local_roughness)

            # IDW
            w = 1.0 / (d_v ** p + 1e-9)
            row = flat_i // nx
            col = flat_i % nx
            grid[row, col] = float(np.sum(w * z_v) / np.sum(w))

        nan_pct = np.isnan(grid).sum() / grid.size * 100
        logger.info(f"  Interpolation complete. NaN cells: {nan_pct:.1f}%")

        if nan_pct > 10:
            logger.warning("More than 10%% of cells are empty. "
                           "Try increasing search_radius or reducing resolution.")

        # Fill residual NaN cells using nearest non-NaN neighbour
        grid = _fill_nan_nearest(grid)

        return x, y, grid


def _fill_nan_nearest(grid: np.ndarray) -> np.ndarray:
    """Fill NaN cells by nearest valid neighbour (simple inpainting)."""
    nan_mask = np.isnan(grid)
    if not nan_mask.any():
        return grid

    rows, cols = np.indices(grid.shape)
    valid_r = rows[~nan_mask]
    valid_c = cols[~nan_mask]
    valid_z = grid[~nan_mask]

    nan_r = rows[nan_mask]
    nan_c = cols[nan_mask]

    fill_tree = cKDTree(np.column_stack([valid_r, valid_c]))
    _, nn_idx = fill_tree.query(np.column_stack([nan_r, nan_c]), k=1)
    grid[nan_mask] = valid_z[nn_idx]

    return grid


# ─────────────────────────────────────────────
#  4. Hydrological Conditioning
# ─────────────────────────────────────────────

def condition_dtm_whitebox(input_tif: str, output_tif: str) -> str:
    """
    Fill depressions (sinks) using WhiteboxTools to ensure proper flow routing.

    Args:
        input_tif: Path to raw DTM GeoTIFF.
        output_tif: Path for hydrologically conditioned output.

    Returns:
        output_tif path.
    """
    if not WHITEBOX_AVAILABLE:
        raise ImportError("whitebox package is not installed. "
                          "Run: pip install whitebox")

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False
    logger.info("  Filling depressions with WhiteboxTools …")
    wbt.fill_depressions(
        dem=input_tif,
        output=output_tif,
        fix_flats=True
    )
    logger.info(f"  Conditioned DTM saved: {output_tif}")
    return output_tif


def condition_dtm_scipy(input_tif: str, output_tif: str,
                        iterations: int = 3) -> str:
    """
    Fallback sink-filling using iterative minimum-smoothing when WhiteboxTools
    is unavailable.  Less accurate than WhiteboxTools but functional.

    Args:
        input_tif: Path to raw DTM GeoTIFF.
        output_tif: Path for conditioned output.
        iterations: Number of smoothing passes.

    Returns:
        output_tif path.
    """
    logger.warning("WhiteboxTools unavailable — using scipy fallback for "
                   "hydrological conditioning (less accurate).")

    with rasterio.open(input_tif) as src:
        grid = src.read(1).astype(np.float32)
        meta = src.meta.copy()
        nodata = src.nodata

    if nodata is not None:
        valid = grid != nodata
    else:
        valid = np.ones_like(grid, dtype=bool)

    for _ in range(iterations):
        if SCIPY_NDIMAGE_AVAILABLE:
            from scipy.ndimage import minimum_filter
            local_min = minimum_filter(grid, size=3)
        else:
            local_min = grid  # no-op if scipy.ndimage not available either

        # Raise depressions to local minimum of their neighbourhood
        depression = (grid < local_min) & valid
        grid[depression] = local_min[depression]

    meta.update(dtype=rasterio.float32)
    with rasterio.open(output_tif, "w", **meta) as dst:
        dst.write(grid, 1)

    logger.info(f"  Conditioned DTM saved (scipy fallback): {output_tif}")
    return output_tif


def condition_dtm(input_tif: str, output_tif: str) -> str:
    """
    Condition a DTM for hydrological routing.
    Uses WhiteboxTools if available, otherwise falls back to scipy.
    """
    if WHITEBOX_AVAILABLE:
        return condition_dtm_whitebox(input_tif, output_tif)
    return condition_dtm_scipy(input_tif, output_tif)


# ─────────────────────────────────────────────
#  5. GeoTIFF Writer
# ─────────────────────────────────────────────

def write_geotiff(output_path: str,
                  grid: np.ndarray,
                  x: np.ndarray,
                  y: np.ndarray,
                  crs=None,
                  nodata: float = -9999.0) -> str:
    """
    Write a 2-D elevation grid to a GeoTIFF file with proper georeferencing.

    Args:
        output_path: Destination file path (.tif / .tiff).
        grid: 2-D float array (rows = south→north if y is ascending).
        x: 1-D array of column centre X coordinates.
        y: 1-D array of row centre Y coordinates.
        crs: Coordinate reference system. Can be an EPSG string like
             'EPSG:32644', a pyproj CRS object, or None.
        nodata: Value to use for missing data cells.

    Returns:
        output_path
    """
    if len(x) < 2 or len(y) < 2:
        raise ValueError("Grid must have at least 2 rows and 2 columns.")

    res_x = float(x[1] - x[0])
    res_y = float(y[1] - y[0])  # positive if y is ascending

    # from_origin expects (west, north, xsize, ysize) with ysize positive
    # If y is ascending the "north" edge is y[-1] + half_cell
    transform = from_origin(
        west=float(x[0]) - res_x / 2,
        north=float(y[-1]) + abs(res_y) / 2,
        xsize=abs(res_x),
        ysize=abs(res_y)
    )

    # Replace NaN with nodata value
    out_grid = np.where(np.isnan(grid), nodata, grid).astype(np.float32)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with rasterio.open(
        output_path, "w",
        driver="GTiff",
        height=grid.shape[0],
        width=grid.shape[1],
        count=1,
        dtype=rasterio.float32,
        crs=crs,
        transform=transform,
        nodata=nodata,
        compress="lzw"       # lossless compression, reduces file size ~3×
    ) as dst:
        dst.write(out_grid, 1)

    logger.info(f"  GeoTIFF written: {output_path} "
                f"({grid.shape[1]}×{grid.shape[0]} px, res={abs(res_x):.2f}m)")
    return output_path


# ─────────────────────────────────────────────
#  6. Validation Utilities
# ─────────────────────────────────────────────

def validate_dtm(dtm_path: str, reference_points: np.ndarray = None) -> dict:
    """
    Run basic quality checks on the generated DTM.

    Args:
        dtm_path: Path to the GeoTIFF DTM.
        reference_points: Optional (M, 3) array of surveyed check points.

    Returns:
        Dictionary with validation metrics.
    """
    results = {}

    with rasterio.open(dtm_path) as src:
        grid = src.read(1).astype(np.float32)
        nodata = src.nodata
        transform = src.transform
        crs = src.crs

    valid = grid != nodata if nodata is not None else np.ones_like(grid, dtype=bool)
    valid_vals = grid[valid]

    results["file"] = dtm_path
    results["crs"] = str(crs)
    results["resolution_m"] = abs(transform.a)
    results["rows"] = grid.shape[0]
    results["cols"] = grid.shape[1]
    results["nodata_pct"] = float((~valid).sum() / valid.size * 100)
    results["z_min"] = float(valid_vals.min()) if valid_vals.size else None
    results["z_max"] = float(valid_vals.max()) if valid_vals.size else None
    results["z_mean"] = float(valid_vals.mean()) if valid_vals.size else None
    results["z_std"] = float(valid_vals.std()) if valid_vals.size else None
    results["pass"] = results["nodata_pct"] < 5.0

    # Optional RMSE against reference points
    if reference_points is not None and len(reference_points) > 0:
        from rasterio.sample import sample_gen
        coords = [(float(p[0]), float(p[1])) for p in reference_points]
        sampled = np.array([v[0] for v in src.sample(coords)])

        # Re-open to sample (src was closed above)
        with rasterio.open(dtm_path) as src2:
            sampled = np.array([v[0] for v in src2.sample(coords)])

        ref_z = reference_points[:, 2]
        diff = sampled - ref_z
        valid_check = sampled != (nodata if nodata else -9999.0)
        if valid_check.sum() > 0:
            results["rmse_m"] = float(np.sqrt(np.mean(diff[valid_check] ** 2)))
            results["mae_m"] = float(np.mean(np.abs(diff[valid_check])))
            results["max_error_m"] = float(np.abs(diff[valid_check]).max())

    return results


# ─────────────────────────────────────────────
#  7. Top-level build_dtm function (Terra Pravah entry point)
# ─────────────────────────────────────────────

def build_dtm(las_path: str,
              output_tif: str,
              resolution: float = 1.0,
              epsg: str = None,
              cell_sizes: list = None,
              base_slope: float = 0.5,
              constant: float = 0.2,
              max_points: int = 12,
              search_radius: float = None,
              downsample: bool = True,
              target_density: float = 10.0,
              progress_callback=None) -> dict:
    """
    Full pipeline: LAS → ground filter → IDW interpolation → GeoTIFF.

    Note: Hydrological conditioning is NOT applied here.
    Call condition_dtm(output_tif, conditioned_tif) separately (DTMBuilderService
    handles this so the raw and conditioned files are kept distinct).

    Args:
        las_path: Path to input .las file.
        output_tif: Path for the output raw DTM GeoTIFF.
        resolution: Grid cell size in metres (default 1.0).
        epsg: EPSG code string, e.g. 'EPSG:32644'.  If None, the CRS from
              the LAS header is used (if present).
        cell_sizes: PMF window sizes in metres.
        base_slope: PMF slope parameter.
        constant: PMF baseline threshold.
        max_points: IDW nearest neighbours.
        search_radius: IDW search radius in metres.
        downsample: Whether to thin the point cloud before processing.
        target_density: Target points/m² after downsampling.
        progress_callback: Optional callable(pct: int, message: str).

    Returns:
        Dictionary with metadata: bounds, point counts, output path, etc.
    """
    def _progress(pct, msg):
        logger.info(f"[{pct:3d}%] {msg}")
        if progress_callback:
            progress_callback(pct, msg)

    _progress(0, "Starting DTM build pipeline …")

    # ── Step 1: Read LAS ──────────────────────────────────────────────────
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
            logger.warning("  CRS not found in LAS header. "
                           "Output GeoTIFF will lack projection info.")

    # ── Step 2: Optional downsampling ────────────────────────────────────
    if downsample and not pre_filtered:
        _progress(15, "Downsampling point cloud …")
        points = downsample_points(points, target_density=target_density, method="grid")

    # ── Step 3: Ground extraction ─────────────────────────────────────────
    if not pre_filtered:
        _progress(25, "Extracting ground points (PMF) …")
        extractor = GroundPointExtractor(
            cell_sizes=cell_sizes or [1, 2, 4, 8],
            base_slope=base_slope,
            constant=constant
        )
        ground_points = extractor.extract(points)
    else:
        ground_points = points
        _progress(25, "Using pre-classified ground points from LAS.")

    if len(ground_points) == 0:
        raise RuntimeError("No ground points found. "
                           "Adjust PMF parameters (base_slope / constant).")

    # ── Step 4: Compute bounds ────────────────────────────────────────────
    xmin = float(ground_points[:, 0].min())
    xmax = float(ground_points[:, 0].max())
    ymin = float(ground_points[:, 1].min())
    ymax = float(ground_points[:, 1].max())
    bounds = (xmin, xmax, ymin, ymax)
    logger.info(f"  Bounds: X [{xmin:.2f} – {xmax:.2f}], "
                f"Y [{ymin:.2f} – {ymax:.2f}]")

    # ── Step 5: IDW interpolation ─────────────────────────────────────────
    _progress(40, "Interpolating DTM (IDW) …")
    interpolator = IDWInterpolator(
        resolution=resolution,
        max_points=max_points,
        search_radius=search_radius or resolution * 5
    )
    x, y, grid = interpolator.interpolate(ground_points, bounds)

    # ── Step 6: Write GeoTIFF ─────────────────────────────────────────────
    _progress(85, "Writing GeoTIFF …")
    write_geotiff(output_tif, grid, x, y, crs=crs)

    _progress(100, f"DTM build complete → {output_tif}")

    return {
        "output_tif": output_tif,
        "crs": crs,
        "bounds": bounds,
        "resolution_m": resolution,
        "total_input_points": total_points,
        "ground_points": len(ground_points),
        "grid_shape": grid.shape,
        "pre_filtered": pre_filtered,
    }
