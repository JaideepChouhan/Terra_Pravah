# DTM Builder — Integration Guide for Terra Pravah

This guide walks you through every step needed to plug `dtm_builder.py`
into your existing Terra Pravah codebase.

---

## 1. Install New Dependencies

Add the following packages to your `requirements.txt`:

```
laspy>=2.4
numpy>=1.24
scipy>=1.11
rasterio>=1.3
whitebox>=2.1
```

Then install:

```bash
source .venv/bin/activate
pip install laspy numpy scipy rasterio whitebox
```

Verify WhiteboxTools downloaded correctly (it auto-downloads a ~120 MB binary on first run):

```bash
python -c "import whitebox; wbt = whitebox.WhiteboxTools(); print(wbt.version())"
```

---

## 2. Place the File in Your Project

Copy `dtm_builder.py` into your services folder:

```
AIR_Terra_Pravah/
└── backend/
    └── services/
        ├── drainage_service.py        ← existing
        ├── visualization_service.py   ← existing
        ├── email_service.py           ← existing
        ├── dtm_builder.py             ← NEW (copy here)
        └── dtm_builder_service.py     ← NEW (create next)
```

---

## 3. Create `dtm_builder_service.py`

This thin wrapper is the bridge between your Flask API and `dtm_builder.py`.
Create `backend/services/dtm_builder_service.py`:

```python
"""
dtm_builder_service.py
Orchestrates the full LAS → conditioned GeoTIFF pipeline
and exposes it to the Flask API layer.
"""

import os
import logging
import tempfile

from .dtm_builder import build_dtm, condition_dtm, validate_dtm

logger = logging.getLogger(__name__)


class DTMBuilderService:
    """
    High-level service called by the Flask API.

    Usage:
        service = DTMBuilderService(
            upload_folder=app.config['UPLOAD_FOLDER'],
            results_folder=app.config['RESULTS_FOLDER']
        )
        result = service.process_las("mycloud.las", resolution=1.0, epsg="EPSG:32644")
    """

    def __init__(self, upload_folder: str, results_folder: str):
        self.upload_folder = upload_folder
        self.results_folder = results_folder
        os.makedirs(results_folder, exist_ok=True)

    def process_las(self,
                    las_filename: str,
                    resolution: float = 1.0,
                    epsg: str = None,
                    progress_callback=None) -> dict:
        """
        Full pipeline: LAS → ground filter → IDW → sink-fill → GeoTIFF.

        Args:
            las_filename: Filename (not full path) of the uploaded .las file.
            resolution:   Grid cell size in metres.
            epsg:         CRS string like 'EPSG:32644'. None = auto-detect.
            progress_callback: Optional callable(pct, message).

        Returns:
            dict with keys: dtm_path, validation, metadata
        """
        las_path = os.path.join(self.upload_folder, las_filename)
        if not os.path.exists(las_path):
            raise FileNotFoundError(f"LAS file not found: {las_path}")

        base = os.path.splitext(las_filename)[0]

        # Use a temp dir for the raw (un-conditioned) DTM
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_tif = os.path.join(tmpdir, f"{base}_raw.tif")
            conditioned_tif = os.path.join(
                self.results_folder, f"{base}_dtm.tif"
            )

            # ── Step A: Build raw DTM ──────────────────────────────────────
            def _relay_progress(pct, msg):
                # Scale step A to 0-80%
                scaled = int(pct * 0.80)
                if progress_callback:
                    progress_callback(scaled, msg)

            metadata = build_dtm(
                las_path=las_path,
                output_tif=raw_tif,
                resolution=resolution,
                epsg=epsg,
                progress_callback=_relay_progress,
            )

            # ── Step B: Hydrological conditioning ────────────────────────
            if progress_callback:
                progress_callback(82, "Conditioning DTM (filling sinks) …")

            condition_dtm(raw_tif, conditioned_tif)

        # ── Step C: Validate ──────────────────────────────────────────────
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
```

---

## 4. Add the API Endpoint

Open `backend/api/uploads.py` and add the new route **alongside** your
existing upload routes:

```python
# ── Add these imports at the top ─────────────────────────────────────────────
from flask import Blueprint, request, jsonify, current_app
from backend.services.dtm_builder_service import DTMBuilderService

uploads_bp = Blueprint("uploads", __name__)   # already exists — don't duplicate


# ── New route ─────────────────────────────────────────────────────────────────
@uploads_bp.route("/build-dtm", methods=["POST"])
def build_dtm_from_las():
    """
    POST /api/uploads/build-dtm
    Body (JSON):
        {
            "filename":   "survey_site.las",   // required
            "resolution": 1.0,                 // optional, metres
            "epsg":       "EPSG:32644"         // optional
        }
    Returns:
        { "dtm_path": "...", "validation": {...}, "metadata": {...} }
    """
    data = request.get_json(force=True)

    filename   = data.get("filename")
    resolution = float(data.get("resolution", 1.0))
    epsg       = data.get("epsg")          # e.g. "EPSG:32644" or null

    if not filename:
        return jsonify({"error": "filename is required"}), 400

    service = DTMBuilderService(
        upload_folder=current_app.config["UPLOAD_FOLDER"],
        results_folder=current_app.config["RESULTS_FOLDER"],
    )

    try:
        result = service.process_las(filename, resolution, epsg)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception("DTM build failed")
        return jsonify({"error": str(e)}), 500

    return jsonify(result), 200
```

---

## 5. Register the Blueprint (if not already registered)

In `backend/app.py`, ensure `uploads_bp` is registered:

```python
from backend.api.uploads import uploads_bp
app.register_blueprint(uploads_bp, url_prefix="/api/uploads")
```

---

## 6. Connect the DTM to the Existing Analysis Pipeline

After the DTM is built, you can feed it directly into
`DrainageAnalysisService`. Here is a combined helper you can call from
your frontend or a Celery task:

```python
from backend.services.dtm_builder_service import DTMBuilderService
from backend.services.drainage_service import DrainageAnalysisService

def run_full_pipeline(las_filename, output_dir,
                      resolution=1.0, epsg=None,
                      runoff_coeff=0.5, storm_years=10,
                      progress_callback=None):
    """
    End-to-end pipeline:
        .las → DTM (conditioned GeoTIFF) → drainage network analysis
    """
    # 1. Build DTM
    dtm_service = DTMBuilderService(
        upload_folder="uploads",
        results_folder=output_dir,
    )
    dtm_result = dtm_service.process_las(
        las_filename, resolution, epsg,
        progress_callback=lambda p, m: progress_callback(int(p * 0.5), m)
        if progress_callback else None,
    )

    dtm_path = dtm_result["dtm_path"]

    # 2. Run drainage analysis on the freshly-built DTM
    analysis_service = DrainageAnalysisService(
        dtm_path=dtm_path,
        output_dir=output_dir,
        config={
            "runoff_coefficient": runoff_coeff,
            "design_storm_years": storm_years,
        },
    )

    def _relay(p, m):
        if progress_callback:
            progress_callback(50 + int(p * 0.5), m)

    analysis_result = analysis_service.run_full_analysis(
        progress_callback=_relay
    )

    return {
        "dtm": dtm_result,
        "drainage": analysis_result,
    }
```

---

## 7. Frontend: Trigger the Build

In your React frontend (e.g. `frontend/src/pages/dashboard/Analysis.tsx`),
call the new endpoint after a .las file is uploaded:

```typescript
// After upload succeeds, kick off DTM build
const buildDTM = async (filename: string, resolution: number, epsg?: string) => {
  const response = await fetch("/api/uploads/build-dtm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename, resolution, epsg }),
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.error ?? "DTM build failed");
  }

  const result = await response.json();
  // result.dtm_path is the conditioned GeoTIFF path
  // Pass it to your existing analysis trigger
  return result;
};
```

---

## 8. Configuration Options Reference

You can pass these parameters to `build_dtm()` or via the API JSON body:

| Parameter        | Type    | Default | Description                                         |
|------------------|---------|---------|-----------------------------------------------------|
| `resolution`     | float   | `1.0`   | Grid cell size in metres                            |
| `epsg`           | string  | `null`  | CRS, e.g. `"EPSG:32644"` (UTM 44N — common India)  |
| `cell_sizes`     | list    | `[1,2,4,8]` | PMF window sizes in metres                    |
| `base_slope`     | float   | `0.5`   | Increase for very rough/hilly terrain               |
| `constant`       | float   | `0.2`   | Minimum height threshold (metres)                   |
| `max_points`     | int     | `12`    | IDW nearest-neighbour count                         |
| `search_radius`  | float   | `5×res` | IDW search radius in metres                         |
| `downsample`     | bool    | `true`  | Thin point cloud before processing (recommended)    |
| `target_density` | float   | `10.0`  | Points per m² after downsampling                   |

### Tuning Tips

**Flat terrain (plains, paddy fields)**
```python
build_dtm(..., cell_sizes=[0.5, 1, 2], base_slope=0.3, constant=0.1)
```

**Hilly/forested terrain**
```python
build_dtm(..., cell_sizes=[2, 4, 8, 16], base_slope=0.8, constant=0.3)
```

**High-density lidar (>50 pts/m²) — speed up processing**
```python
build_dtm(..., downsample=True, target_density=8.0)
```

**Large files (>400 MB) — reduce memory usage**
```python
build_dtm(..., resolution=2.0, downsample=True, target_density=5.0)
```

---

## 9. Folder Structure After Integration

```
AIR_Terra_Pravah/
└── backend/
    └── services/
        ├── dtm_builder.py             ← Core pipeline (new)
        ├── dtm_builder_service.py     ← Flask-facing wrapper (new)
        ├── drainage_service.py        ← Unchanged
        ├── visualization_service.py   ← Unchanged
        └── email_service.py           ← Unchanged
```

---

## 10. Quick Validation Test

After copying the files, run this from the project root to confirm
everything is wired up correctly:

```bash
# Unit-level smoke test
python - <<'EOF'
import numpy as np
from backend.services.dtm_builder import (
    GroundPointExtractor, IDWInterpolator, write_geotiff
)

# Synthetic 100-point cloud
rng = np.random.default_rng(42)
pts = np.column_stack([
    rng.uniform(0, 100, 100),
    rng.uniform(0, 100, 100),
    rng.uniform(10, 15, 100),   # flat-ish terrain
])

ground = GroundPointExtractor().extract(pts)
print(f"Ground points: {len(ground)}")

x, y, grid = IDWInterpolator(resolution=5.0).interpolate(
    ground, (0, 100, 0, 100)
)
print(f"Grid shape: {grid.shape}, NaN: {np.isnan(grid).sum()}")
write_geotiff("/tmp/test_dtm.tif", grid, x, y)
print("GeoTIFF written OK — integration test passed!")
EOF
```

You should see output ending with `integration test passed!`.

---

## 11. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `ImportError: laspy` | Package not installed | `pip install laspy` |
| `No ground points extracted` | PMF too strict | Increase `base_slope` (try `0.8`) |
| `>10% NaN cells in grid` | Low point density near edges | Increase `search_radius` or use `resolution=2.0` |
| `whitebox` hangs / no output | Java not available | `sudo apt install default-jre` (Linux) |
| `MemoryError` on 500 MB file | Insufficient RAM | Set `downsample=True, target_density=5.0` |
| `CRS missing in output` | LAS header has no CRS | Pass `epsg="EPSG:32644"` explicitly |
| `DrainageAnalysisService` returns no streams | DTM has no relief | Verify DTM Z-range > 0.5 m with `validate_dtm()` |
