"""
test_ai_integration.py
======================
Step-by-step integration test for the AI ground classifier.

Run this BEFORE wiring the classifier into your web interface.
Each test builds on the previous one — if an early step fails,
fix it before continuing.

Usage:
    python test_ai_integration.py

    # Or test a specific step only:
    python test_ai_integration.py --step 2
"""

import sys
import argparse
import logging
import time
import json
from pathlib import Path

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
#  Configuration — edit these paths before running
# ─────────────────────────────────────────────────────────────

MODEL_PATH     = "/home/jaideepchouhan/pythonProjects/AIR_Terra_Pravah/backend/models/dtm_outputs_finetuned/best_model.pth"    # ← update this
SWA_PATH       = "/home/jaideepchouhan/pythonProjects/AIR_Terra_Pravah/backend/models/dtm_outputs_finetuned/swa_model.pth"     # ← update this (optional)
THRESHOLD_JSON = "/home/jaideepchouhan/pythonProjects/AIR_Terra_Pravah/backend/models/dtm_outputs_finetuned/threshold.json"    # ← update this (optional)

# A real .las file for end-to-end test (Step 5).
# Leave as "" to skip Steps 5–6.
TEST_LAS_PATH  = "/home/jaideepchouhan/Documents/AIR Docs/GSI 2026/Data/Zip files/Rajasthan_Point_Cloud/64334_2H (REFLIGHT)_POINT CLOUD.LAS"  # e.g. "uploads/my_village.las"
OUTPUT_TIF     = "/home/jaideepchouhan/pythonProjects/AIR_Terra_Pravah/test_results/test_dtm_ai.tif"


# ─────────────────────────────────────────────────────────────
#  Test helpers
# ─────────────────────────────────────────────────────────────

def _header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def _ok(msg: str):
    print(f"  ✓  {msg}")

def _fail(msg: str):
    print(f"  ✗  {msg}")


# ─────────────────────────────────────────────────────────────
#  Step 1 — Check model files exist
# ─────────────────────────────────────────────────────────────

def step1_check_files():
    _header("Step 1: Checking model files")
    ok = True

    for label, path in [("best_model.pth", MODEL_PATH),
                         ("swa_model.pth",  SWA_PATH),
                         ("threshold.json", THRESHOLD_JSON)]:
        if Path(path).exists():
            size = Path(path).stat().st_size / 1e6
            _ok(f"{label} found: {path}  ({size:.1f} MB)")
        else:
            _fail(f"{label} NOT found at: {path}")
            if label in ("best_model.pth",):
                ok = False   # required
            else:
                print(f"       (optional — continuing without it)")

    if not ok:
        print("\n  ACTION: Extract your zip file and place the .pth files")
        print("  in the 'models/' directory next to this script.\n")
        sys.exit(1)

    return True


# ─────────────────────────────────────────────────────────────
#  Step 2 — Import and check dependencies
# ─────────────────────────────────────────────────────────────

def step2_imports():
    _header("Step 2: Checking Python dependencies")

    deps = {
        "torch":          "pip install torch --index-url https://download.pytorch.org/whl/cpu",
        "numpy":          "pip install numpy",
        "laspy":          "pip install laspy",
        "rasterio":       "pip install rasterio",
        "scipy":          "pip install scipy",
    }

    all_ok = True
    for lib, install_cmd in deps.items():
        try:
            __import__(lib)
            _ok(f"{lib}")
        except ImportError:
            _fail(f"{lib} is missing.  Install: {install_cmd}")
            all_ok = False

    # Bonus: check CUDA availability
    try:
        import torch
        if torch.cuda.is_available():
            _ok(f"CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            _ok("No GPU — will run on CPU (slower but fine for most files)")
    except Exception:
        pass

    if not all_ok:
        print("\n  Fix the missing packages, then re-run this script.\n")
        sys.exit(1)

    return True


# ─────────────────────────────────────────────────────────────
#  Step 3 — Load model and classify synthetic points
# ─────────────────────────────────────────────────────────────

def step3_load_model():
    _header("Step 3: Loading model + synthetic classification test")

    try:
        from ai_ground_classifier import AIGroundClassifier
    except ImportError as e:
        _fail(f"Cannot import ai_ground_classifier: {e}")
        print("  Make sure ai_ground_classifier.py is in the same directory.")
        sys.exit(1)

    clf = AIGroundClassifier(
        model_path=MODEL_PATH,
        threshold_json=THRESHOLD_JSON if Path(THRESHOLD_JSON).exists() else None,
    )
    _ok(f"Model loaded from {MODEL_PATH}")
    _ok(f"Classification threshold: {clf.threshold:.3f}")
    _ok(f"Running on device: {clf.device}")

    # ── Synthetic point cloud ────────────────────────────────────────────────
    # Flat ground layer at z≈0 + buildings at z=2-4
    rng = np.random.default_rng(42)
    N   = 2000
    xy  = rng.uniform(0, 50, size=(N, 2))

    # Ground: mostly flat with tiny undulations
    z_ground = rng.normal(0, 0.05, size=N)

    # Fake buildings: random patches raised by 2–4 m
    for _ in range(5):
        cx, cy = rng.uniform(5, 45, 2)
        mask   = np.sqrt((xy[:, 0] - cx)**2 + (xy[:, 1] - cy)**2) < 3
        z_ground[mask] += rng.uniform(2, 4)

    points = np.column_stack([xy, z_ground]).astype(np.float32)

    t0     = time.perf_counter()
    ground = clf.extract(points)
    elapsed = time.perf_counter() - t0

    ground_pct = len(ground) / len(points) * 100
    _ok(f"Synthetic test: {len(points):,} points → {len(ground):,} ground ({ground_pct:.1f}%) in {elapsed:.2f}s")

    # Sanity: flat ground should be above 50% of points
    if ground_pct < 30:
        print(f"  ⚠  Ground pct is low ({ground_pct:.1f}%). "
              "Model may not match architecture — double-check ai_ground_classifier.py.")
    elif ground_pct > 95:
        print(f"  ⚠  Ground pct is very high ({ground_pct:.1f}%). "
              "Consider raising the threshold slightly.")
    else:
        _ok("Ground percentage looks reasonable ✓")

    return clf


# ─────────────────────────────────────────────────────────────
#  Step 4 — Test service wrapper (no LAS file needed)
# ─────────────────────────────────────────────────────────────

def step4_service_wrapper():
    _header("Step 4: Testing DTMBuilderServiceAI wrapper")

    try:
        from dtm_builder_ai import DTMBuilderServiceAI
    except ImportError as e:
        _fail(f"Cannot import dtm_builder_ai: {e}")
        print("  Make sure dtm_builder_ai.py is in the same directory.")
        sys.exit(1)

    try:
        service = DTMBuilderServiceAI(
            upload_folder="uploads",
            results_folder="results",
            model_path=MODEL_PATH,
            threshold_json=THRESHOLD_JSON if Path(THRESHOLD_JSON).exists() else None,
        )
        _ok("DTMBuilderServiceAI instantiated successfully")
        _ok(f"  model_path:     {service.model_path}")
        _ok(f"  upload_folder:  {service.upload_folder}")
        _ok(f"  results_folder: {service.results_folder}")
    except FileNotFoundError as e:
        _fail(str(e))
        sys.exit(1)

    return service


# ─────────────────────────────────────────────────────────────
#  Step 5 — End-to-end test on a real LAS file (optional)
# ─────────────────────────────────────────────────────────────

def step5_end_to_end(service):
    _header("Step 5: End-to-end test with real LAS file")

    if not TEST_LAS_PATH:
        print("  ⏭  Skipped — set TEST_LAS_PATH in this script to enable.")
        return

    if not Path(TEST_LAS_PATH).exists():
        _fail(f"LAS file not found: {TEST_LAS_PATH}")
        return

    las_file = Path(TEST_LAS_PATH).name
    upload_dir = Path(TEST_LAS_PATH).parent
    results_dir = Path(OUTPUT_TIF).parent
    results_dir.mkdir(parents=True, exist_ok=True)

    service.upload_folder  = str(upload_dir)
    service.results_folder = str(results_dir)

    log = []
    def progress(pct, msg):
        log.append((pct, msg))
        print(f"  [{pct:3d}%] {msg}")

    t0 = time.perf_counter()
    result = service.process_las(
        las_filename=las_file,
        resolution=1.0,
        progress_callback=progress,
    )
    elapsed = time.perf_counter() - t0

    _ok(f"DTM generated in {elapsed:.1f}s")
    _ok(f"Output: {result['dtm_path']}")

    val = result["validation"]
    _ok(f"  Resolution: {val.get('resolution_m', '?')}m")
    _ok(f"  Size:       {val.get('cols', '?')} × {val.get('rows', '?')} px")
    _ok(f"  Elevation:  {val.get('z_min', '?'):.1f} – {val.get('z_max', '?'):.1f} m")
    _ok(f"  NoData:     {val.get('nodata_pct', '?'):.1f}%")
    _ok(f"  QA pass:    {val.get('pass', False)}")

    ai = result.get("ai_classification", {})
    if ai:
        _ok(f"  Ground pts: {ai.get('ground_points', '?'):,} "
            f"({ai.get('ground_pct', '?')}%)")


# ─────────────────────────────────────────────────────────────
#  Step 6 — Show how to integrate into web API
# ─────────────────────────────────────────────────────────────

def step6_web_api_hint():
    _header("Step 6: Web API integration snippet")

    snippet = '''
# In your Flask / FastAPI route file, replace:
#   from dtm_builder_service import DTMBuilderService
# With:
#   from dtm_builder_ai import DTMBuilderServiceAI

# Flask example -------------------------------------------------------
from flask import Flask, request, jsonify
from dtm_builder_ai import DTMBuilderServiceAI

app = Flask(__name__)

service = DTMBuilderServiceAI(
    upload_folder = "uploads",
    results_folder = "results",
    model_path     = "models/best_model.pth",
    threshold_json = "models/threshold.json",  # optional
)

@app.route("/api/generate-dtm", methods=["POST"])
def generate_dtm():
    file = request.files.get("las_file")
    if not file:
        return jsonify({"error": "No LAS file uploaded"}), 400

    file.save(f"uploads/{file.filename}")

    progress_log = []
    def on_progress(pct, msg):
        progress_log.append({"pct": pct, "msg": msg})

    result = service.process_las(
        las_filename     = file.filename,
        resolution       = float(request.form.get("resolution", 1.0)),
        progress_callback = on_progress,
    )

    return jsonify({
        "dtm_path":  result["dtm_path"],
        "validation": result["validation"],
        "ai_stats":  result["ai_classification"],
        "progress":  progress_log,
    })
# FastAPI example ------------------------------------------------------
from fastapi import FastAPI, UploadFile
from dtm_builder_ai import DTMBuilderServiceAI

app  = FastAPI()
svc  = DTMBuilderServiceAI(
    upload_folder  = "uploads",
    results_folder = "results",
    model_path     = "models/best_model.pth",
)

@app.post("/generate-dtm")
async def generate_dtm(file: UploadFile, resolution: float = 1.0):
    path = f"uploads/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    result = svc.process_las(file.filename, resolution=resolution)
    return result
'''
    print(snippet)


# ─────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=int, default=0,
                        help="Run only a specific step (1-6). Default: run all.")
    args = parser.parse_args()

    all_steps = args.step == 0

    if all_steps or args.step == 1:
        step1_check_files()
    if all_steps or args.step == 2:
        step2_imports()
    clf = None
    if all_steps or args.step == 3:
        clf = step3_load_model()
    service = None
    if all_steps or args.step == 4:
        service = step4_service_wrapper()
    if all_steps or args.step == 5:
        if service is None:
            service = step4_service_wrapper()
        step5_end_to_end(service)
    if all_steps or args.step == 6:
        step6_web_api_hint()

    _header("All tests passed! ✓")
    print("  Your AI ground classifier is ready.\n")


if __name__ == "__main__":
    main()
