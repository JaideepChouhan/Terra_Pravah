"""
ai_ground_classifier.py
========================
AI-powered ground point classification using the trained DTMPointNet2 model.

Architecture is reverse-engineered from the saved checkpoint weight shapes in
dtm_outputs_finetuned/best_model.pth. DO NOT change the DTMPointNet2 class
dimensions — they must match the checkpoint exactly.

Part of Terra Pravah v2.3 — MoPR Hackathon Pipeline (AI Ground Filter)
"""

import logging
import json
import os
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.error(
        "PyTorch not found. Install with:\n"
        "  pip install torch --index-url https://download.pytorch.org/whl/cpu"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Geo-feature extractor — must stay identical to Cell 3 of the training notebook
#  (dtm-v6-final.ipynb). DO NOT MODIFY.
# ─────────────────────────────────────────────────────────────────────────────

def _grid(xyz, cell_m, gmax=64):
    xmin, ymin = xyz[:, 0].min(), xyz[:, 1].min()
    xr = xyz[:, 0].max() - xmin + 1e-6
    yr = xyz[:, 1].max() - ymin + 1e-6
    GW = int(np.clip(xr / cell_m, 8, gmax))
    GH = int(np.clip(yr / cell_m, 8, gmax))
    xi = np.clip(((xyz[:, 0] - xmin) / xr * GW).astype(np.int32), 0, GW - 1)
    yi = np.clip(((xyz[:, 1] - ymin) / yr * GH).astype(np.int32), 0, GH - 1)
    ci = yi * GW + xi
    NC = GW * GH
    z = xyz[:, 2].astype(np.float32)
    c_min = np.full(NC, np.inf, np.float32)
    c_sum = np.zeros(NC, np.float32)
    c_sq  = np.zeros(NC, np.float32)
    c_cnt = np.zeros(NC, np.float32)
    c_max = np.full(NC, -np.inf, np.float32)
    np.minimum.at(c_min, ci, z)
    np.maximum.at(c_max, ci, z)
    np.add.at(c_sum, ci, z)
    np.add.at(c_sq,  ci, z * z)
    np.add.at(c_cnt, ci, 1.)
    empty = c_cnt == 0
    c_cnt[empty] = 1
    c_min[empty] = z.mean()
    c_max[empty] = z.mean()
    c_sum[empty] = z.mean()
    c_sq[empty]  = z.mean() ** 2
    c_mean = c_sum / c_cnt
    c_std  = np.sqrt(np.maximum(c_sq / c_cnt - c_mean ** 2, 0.))
    return ci, c_min, c_std, c_cnt, c_max - c_min, GW, GH


def geo_features(xyz: np.ndarray) -> np.ndarray:
    """
    Compute 6 terrain features per point from raw XYZ coordinates.
    Returns (N, 6) float32 — [dZ_2m, roughness, slope, density, dZ_8m, planarity]
    z-score normalised per tile to match training-time statistics.
    """
    xyz = xyz.astype(np.float32, copy=False)
    ci2, cm2, cs2, cc2, cr2, GW2, GH2 = _grid(xyz, 2.0)
    dz2       = np.clip(xyz[:, 2] - cm2[ci2], 0., None)
    roughness = cs2[ci2]
    cg  = cm2.reshape(GH2, GW2)
    pad = np.pad(cg, 1, mode='edge')
    sg  = np.max(np.stack([
        np.abs(cg - pad[:-2, 1:-1]),
        np.abs(cg - pad[2:,  1:-1]),
        np.abs(cg - pad[1:-1, :-2]),
        np.abs(cg - pad[1:-1,  2:])
    ]), axis=0) / 2.
    slope    = sg.reshape(-1)[ci2]
    density  = cc2[ci2] / (cc2.max() + 1e-6)
    ci8, cm8, _, _, _, _, _ = _grid(xyz, 8.0, 32)
    dz8       = np.clip(xyz[:, 2] - cm8[ci8], 0., None)
    planarity = cs2[ci2] / (cr2[ci2] + 1e-6)
    feat = np.stack([dz2, roughness, slope, density, dz8, planarity], axis=1)
    mu = feat.mean(0, keepdims=True)
    sg = feat.std(0,  keepdims=True) + 1e-6
    return ((feat - mu) / sg).astype(np.float32)


# ─────────────────────────────────────────────────────────────────────────────
#  PointNet++ building blocks — identical to Cell 5 of the training notebook.
#  DO NOT MODIFY.
# ─────────────────────────────────────────────────────────────────────────────

def _fps(xyz, n):
    B, N, _ = xyz.shape
    dev = xyz.device
    c   = torch.zeros(B, n, dtype=torch.long, device=dev)
    d   = torch.full((B, N), 1e10, dtype=torch.float32, device=dev)
    far = torch.randint(0, N, (B,), dtype=torch.long, device=dev)
    bi  = torch.arange(B, dtype=torch.long, device=dev)
    for i in range(n):
        c[:, i] = far
        cc  = xyz[bi, far].unsqueeze(1)
        dd  = ((xyz - cc) ** 2).sum(-1)
        d   = torch.where(dd < d, dd, d)
        far = d.argmax(-1)
    return c


def _idx(p, i):
    B  = p.shape[0]
    bi = torch.arange(B, device=p.device).view(
        [B] + [1] * (i.dim() - 1)).expand_as(i)
    return p[bi, i]


def _ball(nxyz, xyz, r, k):
    d = torch.cdist(nxyz, xyz)
    return torch.where(d <= r, d, d.new_full((), 1e10)).topk(
        k, dim=-1, largest=False).indices


class _MSG(nn.Module):
    def __init__(self, nc, radii, nsamps, ic, specs):
        super().__init__()
        self.nc     = nc
        self.radii  = radii
        self.nsamps = nsamps
        self.mlps   = nn.ModuleList()
        for dims in specs:
            ls, ch = [], ic + 3
            for d in dims:
                ls += [nn.Conv2d(ch, d, 1, bias=False),
                       nn.BatchNorm2d(d),
                       nn.ReLU(True)]
                ch = d
            self.mlps.append(nn.Sequential(*ls))

    def forward(self, xyz, feat):
        ci   = _fps(xyz, self.nc)
        nxyz = _idx(xyz, ci)
        outs = []
        for r, k, mlp in zip(self.radii, self.nsamps, self.mlps):
            idx  = _ball(nxyz, xyz, r, k)
            grp  = _idx(feat, idx)
            rxyz = _idx(xyz, idx) - nxyz.unsqueeze(2)
            grp  = torch.cat([rxyz, grp], -1).permute(0, 3, 2, 1)
            outs.append(mlp(grp).max(2).values)
        return nxyz, torch.cat(outs, 1).permute(0, 2, 1)


class _SA(nn.Module):
    def __init__(self, r, k, ic, dims):
        super().__init__()
        self.r = r
        self.k = k
        ls, ch = [], ic + 3
        for d in dims:
            ls += [nn.Conv2d(ch, d, 1, bias=False),
                   nn.BatchNorm2d(d),
                   nn.ReLU(True)]
            ch = d
        self.mlp = nn.Sequential(*ls)

    def forward(self, xyz, feat):
        nc   = max(1, xyz.shape[1] // 4)
        ci   = _fps(xyz, nc)
        nxyz = _idx(xyz, ci)
        idx  = _ball(nxyz, xyz, self.r, self.k)
        grp  = _idx(feat, idx)
        rxyz = _idx(xyz, idx) - nxyz.unsqueeze(2)
        grp  = torch.cat([rxyz, grp], -1).permute(0, 3, 2, 1)
        return nxyz, self.mlp(grp).max(2).values.permute(0, 2, 1)


class _FP(nn.Module):
    def __init__(self, ic1, ic2, dims):
        super().__init__()
        ls, ch = [], ic1 + ic2
        for d in dims:
            ls += [nn.Conv1d(ch, d, 1, bias=False),
                   nn.BatchNorm1d(d),
                   nn.ReLU(True)]
            ch = d
        self.mlp = nn.Sequential(*ls)

    def forward(self, xyz1, xyz2, feat1, feat2):
        dists = torch.cdist(xyz1, xyz2)
        k     = min(3, xyz2.shape[1])
        w, ii = dists.topk(k, dim=-1, largest=False)
        w     = 1.0 / (w + 1e-8)
        w     = w / w.sum(-1, keepdim=True)
        iF    = _idx(feat2, ii)
        iF    = (iF * w.unsqueeze(-1)).sum(-2)
        out   = torch.cat([feat1, iF], -1).permute(0, 2, 1)
        return self.mlp(out).permute(0, 2, 1)


# ─────────────────────────────────────────────────────────────────────────────
#  DTMPointNet2 — architecture verified against dtm_outputs_finetuned weights
#
#  Channel dimensions derived directly from the RuntimeError weight shapes:
#
#    SA1 branch 0: mlps.0.0.weight [64, 12, 1,1]  → ic+3=12 ✓, out=64
#                  mlps.0.3.weight [64, 64, 1,1]  → 64→64   (2-layer MLP)
#    SA1 branch 1: mlps.1.0.weight [64, 12, 1,1]  → out=64
#                  mlps.1.3.weight [128, 64, 1,1] → 64→128  (2-layer MLP)
#    SA1 concat output = 64 + 128 = 192
#
#    SA2 branch 0: mlps.0.0.weight [128, 195, 1,1] → 195=192+3 ✓, out=128
#                  mlps.0.3.weight [192, 128, 1,1] → 128→192
#    SA2 branch 1: mlps.1.3.weight [256, 128, 1,1] → 128→256
#    SA2 concat output = 192 + 256 = 448
#
#    SA3:          mlp.0.weight [256, 451, 1,1]    → 451=448+3 ✓
#                  (no mlp.6 key → 2-layer MLP)   SA3 output = 512
#
#    FP3 input = 448+512 = 960  ✓  mlp.0.weight [256, 960, 1]
#    FP2 input = 192+256 = 448  ✓  mlp.0.weight [256, 448, 1]
#    FP1:          mlp.6.weight [64, 128, 1]       → 3rd layer → output=64
#    Head:         head.0.weight [64,64,1], head.4.weight [2,64,1] ✓
# ─────────────────────────────────────────────────────────────────────────────

IN_FEAT = 9   # xyz (3) + terrain features (6)


class DTMPointNet2(nn.Module):
    """
    Point cloud ground classifier.
    Input : (B, N, 9)  — xyz + 6 terrain features
    Output: (B, N, 2)  — logits [non-ground, ground]
    """

    def __init__(self, in_feat: int = 9):
        super().__init__()

        # SA1 — 2 radii, 2 branches → concat output 192 channels
        self.sa1 = _MSG(
            nc=512,
            radii=[0.5, 1.5],
            nsamps=[16, 32],
            ic=in_feat,
            specs=[[64, 64], [64, 128]],
        )

        # SA2 — 2 radii, 2 branches (input 192) → concat output 448 channels
        self.sa2 = _MSG(
            nc=128,
            radii=[2.0, 4.0],
            nsamps=[32, 64],
            ic=192,
            specs=[[128, 192], [128, 256]],
        )

        # SA3 — 1 radius, 2-layer MLP (input 448) → output 512 channels
        self.sa3 = _SA(r=8.0, k=32, ic=448, dims=[256, 512])

        # FP3 — input 448+512=960 → output 256 channels
        self.fp3 = _FP(ic1=448, ic2=512, dims=[256, 256])

        # FP2 — input 192+256=448 → output 128 channels
        self.fp2 = _FP(ic1=192, ic2=256, dims=[256, 128])

        # FP1 — input 9+128=137, 3-layer MLP → output 64 channels
        self.fp1 = _FP(ic1=in_feat, ic2=128, dims=[128, 128, 64])

        # Head — 64 → 64 → 2
        self.head = nn.Sequential(
            nn.Conv1d(64, 64, 1, bias=False),
            nn.BatchNorm1d(64),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Conv1d(64, 2, 1),
        )

    def forward(self, pts: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pts: (B, N, 9)
        Returns:
            logits: (B, N, 2)
        """
        xyz0  = pts[:, :, :3]
        feat0 = pts
        xyz1, feat1 = self.sa1(xyz0, feat0)
        xyz2, feat2 = self.sa2(xyz1, feat1)
        xyz3, feat3 = self.sa3(xyz2, feat2)
        feat2 = self.fp3(xyz2, xyz3, feat2, feat3)
        feat1 = self.fp2(xyz1, xyz2, feat1, feat2)
        feat0 = self.fp1(xyz0, xyz1, feat0, feat1)
        return self.head(feat0.permute(0, 2, 1)).permute(0, 2, 1)


# ─────────────────────────────────────────────────────────────────────────────
#  Threshold loader — handles both flat and nested threshold.json formats
# ─────────────────────────────────────────────────────────────────────────────

def _load_threshold(path: str, default: float = 0.5) -> float:
    """
    Load optimal threshold from threshold.json.

    Handles two formats produced by training Cell 9:

    Format A — flat dict (most common, single winner written directly):
        {"threshold": 0.56, "val_accuracy": 0.9397, "val_f1": 0.9073, ...}

    Format B — nested dict (both best and swa models reported):
        {"best": {"threshold": 0.56, "val_accuracy": 0.9397, ...},
         "swa":  {"threshold": 0.53, "val_accuracy": 0.9365, ...}}
    """
    try:
        with open(path) as f:
            tj = json.load(f)

        # Format A — "threshold" key exists at the top level
        if isinstance(tj, dict) and "threshold" in tj:
            thr = float(tj["threshold"])
            logger.info(f"  Loaded threshold={thr:.3f} from {path} "
                        f"(val_accuracy={tj.get('val_accuracy', '?')})")
            return thr

        # Format B — values are nested dicts; pick highest val_accuracy
        if isinstance(tj, dict):
            nested = {k: v for k, v in tj.items() if isinstance(v, dict)}
            if nested:
                best_key = max(nested, key=lambda k: nested[k].get("val_accuracy", 0))
                thr = float(nested[best_key]["threshold"])
                logger.info(f"  Loaded threshold={thr:.3f} from {path} "
                            f"(model='{best_key}', "
                            f"val_accuracy={nested[best_key].get('val_accuracy', '?')})")
                return thr

        logger.warning(f"  threshold.json has an unrecognised format — "
                       f"using default={default}")
        return default

    except Exception as e:
        logger.warning(f"  Could not read threshold.json ({e}) — "
                       f"using default={default}")
        return default


# ─────────────────────────────────────────────────────────────────────────────
#  Public interface
# ─────────────────────────────────────────────────────────────────────────────

class AIGroundClassifier:
    """
    Drop-in replacement for GroundPointExtractor.
    Uses the trained DTMPointNet2 model instead of PMF.

    Example
    -------
    clf = AIGroundClassifier(
        model_path="backend/models/dtm_outputs_finetuned/best_model.pth",
        threshold_json="backend/models/dtm_outputs_finetuned/threshold.json",
    )
    ground_xyz = clf.extract(all_points_xyz)
    """

    def __init__(
        self,
        model_path: str,
        threshold: float = 0.5,
        threshold_json: Optional[str] = None,
        chunk_size: int = 4096,
        device: Optional[str] = None,
    ):
        if not HAS_TORCH:
            raise ImportError(
                "PyTorch is required. Install with:\n"
                "  pip install torch --index-url https://download.pytorch.org/whl/cpu"
            )

        self.chunk_size = chunk_size

        # Resolve device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        logger.info(f"AIGroundClassifier: using device={self.device}")

        # Load threshold
        if threshold_json and Path(threshold_json).exists():
            self.threshold = _load_threshold(threshold_json, default=threshold)
        else:
            self.threshold = threshold
            logger.info(f"  Using threshold={self.threshold} (no threshold.json)")

        # Load model weights
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        self.model = DTMPointNet2(in_feat=IN_FEAT).to(self.device)
        state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state_dict)
        self.model.eval()

        n_params = sum(p.numel() for p in self.model.parameters())
        logger.info(f"  Loaded: {model_path}  ({n_params/1e6:.2f}M parameters)")

    def _build_input_tensor(self, xyz_chunk: np.ndarray) -> torch.Tensor:
        feats = geo_features(xyz_chunk)
        pts   = np.concatenate([xyz_chunk, feats], axis=1)
        return torch.from_numpy(pts).unsqueeze(0).to(self.device)

    @torch.no_grad()
    def _predict_chunk(self, xyz_chunk: np.ndarray) -> np.ndarray:
        t      = self._build_input_tensor(xyz_chunk)
        logits = self.model(t)
        probs  = F.softmax(logits, dim=-1)
        return probs[0, :, 1].cpu().numpy()

    def extract(self, points: np.ndarray) -> np.ndarray:
        """
        Classify every point and return only ground points.
        Drop-in replacement for GroundPointExtractor.extract().

        Args:
            points: (N, 3) numpy array of XYZ coordinates.
        Returns:
            ground_points: (M, 3) array, M <= N.
        """
        if not isinstance(points, np.ndarray) or points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("points must be a (N, 3) numpy array.")

        N = len(points)
        if N == 0:
            return points

        logger.info(f"AIGroundClassifier: classifying {N:,} points …")

        # Normalise XYZ — same pre-processing as GroundDataset in training
        xyz_norm = points.copy().astype(np.float32)
        xyz_norm[:, 0] -= xyz_norm[:, 0].mean()
        xyz_norm[:, 1] -= xyz_norm[:, 1].mean()
        z_range = xyz_norm[:, 2].max() - xyz_norm[:, 2].min() + 1e-6
        xyz_norm[:, 2] = (xyz_norm[:, 2] - xyz_norm[:, 2].min()) / z_range

        # Process in chunks
        all_probs = np.zeros(N, dtype=np.float32)
        rng       = np.random.default_rng(42)
        n_chunks  = (N + self.chunk_size - 1) // self.chunk_size

        for i in range(n_chunks):
            idx = rng.choice(N, self.chunk_size, replace=False) if N > self.chunk_size \
                  else np.arange(N)
            chunk_probs    = self._predict_chunk(xyz_norm[idx])
            all_probs[idx] = np.maximum(all_probs[idx], chunk_probs)
            if (i + 1) % 10 == 0 or (i + 1) == n_chunks:
                logger.info(f"  Chunk {i+1}/{n_chunks} …")

        ground_points = points[all_probs >= self.threshold]
        pct = len(ground_points) / N * 100
        logger.info(f"  Done: {len(ground_points):,} ground ({pct:.1f}%) of {N:,}")

        if len(ground_points) < 100:
            logger.warning(
                f"Only {len(ground_points)} ground points found. "
                "Try lowering threshold (e.g. threshold=0.35)."
            )
        return ground_points

    def extract_with_stats(self, points: np.ndarray) -> Tuple[np.ndarray, dict]:
        ground = self.extract(points)
        return ground, {
            "total_points":  len(points),
            "ground_points": len(ground),
            "ground_pct":    round(len(ground) / max(len(points), 1) * 100, 2),
            "threshold":     self.threshold,
            "device":        str(self.device),
        }

