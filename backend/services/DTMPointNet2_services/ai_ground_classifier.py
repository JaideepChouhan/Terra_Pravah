"""
ai_ground_classifier.py
========================
AI-powered ground point classification using the trained DTMPointNet2 model.

This module replaces the PMF (Progressive Morphological Filter) in dtm_builder.py
with the trained neural network from best_model.pth / swa_model.pth.

The model architecture (DTMPointNet2) and feature extractor (geo_features) are
copied exactly from the training notebook (dtm-v6-final.ipynb) so weights load cleanly.

Part of Terra Pravah v2.3 — MoPR Hackathon Pipeline (AI Ground Filter)

Usage:
    from ai_ground_classifier import AIGroundClassifier

    clf = AIGroundClassifier(model_path="models/best_model.pth")
    ground_xyz = clf.extract_ground(all_points_xyz)
"""

import logging
import json
import os
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
#  PyTorch — required for AI classifier
# ─────────────────────────────────────────────────────────────
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.error(
        "PyTorch not found. Install with:\n"
        "  pip install torch --index-url https://download.pytorch.org/whl/cpu\n"
        "(CPU-only build is fine — inference is fast enough without GPU)"
    )


# ─────────────────────────────────────────────────────────────
#  Geo-feature extractor — copied verbatim from Cell 3 of
#  dtm-v6-final.ipynb so it matches what the model was trained on.
#  DO NOT MODIFY THIS FUNCTION.
# ─────────────────────────────────────────────────────────────

def _grid(xyz, cell_m, gmax=64):
    """Internal helper: build a grid-cell index and per-cell statistics."""
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
    Output: (N, 6) float32 — [dZ_2m, roughness, slope, density, dZ_8m, planarity]
    These are z-score normalised so they match training-time feature statistics.

    IMPORTANT: This must stay identical to Cell 3 of dtm-v6-final.ipynb.
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
    dz8      = np.clip(xyz[:, 2] - cm8[ci8], 0., None)
    planarity = cs2[ci2] / (cr2[ci2] + 1e-6)
    feat = np.stack([dz2, roughness, slope, density, dz8, planarity], axis=1)
    mu = feat.mean(0, keepdims=True)
    sg = feat.std(0,  keepdims=True) + 1e-6
    return ((feat - mu) / sg).astype(np.float32)


# ─────────────────────────────────────────────────────────────
#  DTMPointNet2 architecture — copied verbatim from Cell 5 of
#  dtm-v6-final.ipynb.  DO NOT MODIFY THIS CLASS.
# ─────────────────────────────────────────────────────────────

def _fps(xyz, n):
    """Farthest Point Sampling — selects n representative points."""
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
        self.nc = nc
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


class DTMPointNet2(nn.Module):
    """
    Point cloud ground classifier.
    Input : (B, N, IN_FEAT) tensor where IN_FEAT = 9 (xyz + 6 terrain features)
    Output: (B, N, 2)       logits  [non-ground, ground]
    """
    def __init__(self, in_feat: int = 9):
        super().__init__()
        self.sa1 = _MSG(512, [1.0, 2.0, 4.0], [16, 32, 64], in_feat,
                        [[32, 32, 64], [64, 64, 128], [64, 96, 128]])
        self.sa2 = _MSG(128, [2.0, 4.0, 8.0], [32, 64, 128], 320,
                        [[64, 64, 128], [128, 128, 256], [128, 128, 256]])
        self.sa3 = _SA(8.0, 32, 640, [256, 512, 1024])
        self.fp3 = _FP(640, 1024, [256, 256])
        self.fp2 = _FP(320,  256, [256, 128])
        self.fp1 = _FP(in_feat, 128, [128, 128, 128])
        self.head = nn.Sequential(
            nn.Conv1d(128, 128, 1, bias=False),
            nn.BatchNorm1d(128),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Conv1d(128, 2, 1)
        )

    def forward(self, pts: torch.Tensor) -> torch.Tensor:
        """
        Args:
            pts: (B, N, 9) — xyz in first 3 channels, features in remaining 6.
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


# ─────────────────────────────────────────────────────────────
#  Public interface
# ─────────────────────────────────────────────────────────────

IN_FEAT = 9   # xyz (3) + terrain features (6)


class AIGroundClassifier:
    """
    Drop-in replacement for dtm_builder.GroundPointExtractor.
    Uses the trained DTMPointNet2 model instead of PMF.

    Example
    -------
    clf = AIGroundClassifier(model_path="models/best_model.pth")
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
        """
        Args:
            model_path: Path to best_model.pth or swa_model.pth.
            threshold:  Classification probability cut-off (default 0.5).
                        Overridden if threshold_json is provided.
            threshold_json: Path to threshold.json generated by Cell 9 of the
                            training notebook. If found, the optimal threshold
                            is loaded automatically.
            chunk_size: Points processed in one forward pass (default 4096,
                        matching training max_pts). Lower this if you run out
                        of RAM.
            device:     'cpu', 'cuda', or None (auto-detect).
        """
        if not HAS_TORCH:
            raise ImportError(
                "PyTorch is required. Install with:\n"
                "  pip install torch --index-url https://download.pytorch.org/whl/cpu"
            )

        self.chunk_size = chunk_size
        self.threshold  = threshold

        # ── Resolve device ──────────────────────────────────────────────
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        logger.info(f"AIGroundClassifier: using device={self.device}")

        # ── Load optimal threshold from threshold.json if provided ──────
        if threshold_json and Path(threshold_json).exists():
            try:
                with open(threshold_json) as f:
                    tj = json.load(f)
                # threshold.json stores results for 'best' and 'swa' keys
                # Pick the one with the highest val_accuracy
                best_key = max(tj, key=lambda k: tj[k].get("val_accuracy", 0))
                self.threshold = float(tj[best_key]["threshold"])
                logger.info(
                    f"  Loaded threshold={self.threshold:.3f} "
                    f"from {threshold_json} (model='{best_key}', "
                    f"val_acc={tj[best_key]['val_accuracy']*100:.2f}%)"
                )
            except Exception as e:
                logger.warning(f"  Could not read threshold.json: {e}. "
                               f"Using default threshold={self.threshold}")
        else:
            logger.info(f"  Using threshold={self.threshold} (no threshold.json found)")

        # ── Load model weights ──────────────────────────────────────────
        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}\n"
                "Make sure you extracted best_model.pth from your zip file."
            )

        self.model = DTMPointNet2(in_feat=IN_FEAT).to(self.device)
        state_dict = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()

        n_params = sum(p.numel() for p in self.model.parameters())
        logger.info(
            f"  Loaded model: {model_path}  "
            f"({n_params/1e6:.1f}M parameters)"
        )

    # ── Private helpers ─────────────────────────────────────────────────

    def _build_input_tensor(self, xyz_chunk: np.ndarray) -> torch.Tensor:
        """
        Combine xyz + 6 geo_features into a (1, N, 9) tensor.
        This matches exactly what the model was trained on.
        """
        feats = geo_features(xyz_chunk)          # (N, 6)
        pts   = np.concatenate([xyz_chunk, feats], axis=1)   # (N, 9)
        return torch.from_numpy(pts).unsqueeze(0).to(self.device)  # (1, N, 9)

    @torch.no_grad()
    def _predict_chunk(self, xyz_chunk: np.ndarray) -> np.ndarray:
        """
        Run one forward pass and return per-point ground probability.
        Returns: (N,) float array of ground probabilities.
        """
        t      = self._build_input_tensor(xyz_chunk)
        logits = self.model(t)                     # (1, N, 2)
        probs  = F.softmax(logits, dim=-1)         # (1, N, 2)
        return probs[0, :, 1].cpu().numpy()        # ground class = index 1

    # ── Public API ──────────────────────────────────────────────────────

    def extract(self, points: np.ndarray) -> np.ndarray:
        """
        Drop-in replacement for GroundPointExtractor.extract().
        Classifies every point as ground / non-ground using the AI model.

        Args:
            points: (N, 3) numpy array of XYZ coordinates.

        Returns:
            ground_points: (M, 3) array of ground-only XYZ points, M <= N.
        """
        if not isinstance(points, np.ndarray) or points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("points must be a (N, 3) numpy array of XYZ coordinates.")

        if len(points) == 0:
            logger.warning("AIGroundClassifier.extract(): received empty point array.")
            return points

        N = len(points)
        logger.info(f"AIGroundClassifier: classifying {N:,} points in chunks of {self.chunk_size} …")

        # ── Normalise XYZ to zero-mean, unit-range for numerical stability ──
        # (same pre-processing used in training GroundDataset.__getitem__)
        xyz_norm = points.copy().astype(np.float32)
        xyz_norm[:, 0] -= xyz_norm[:, 0].mean()
        xyz_norm[:, 1] -= xyz_norm[:, 1].mean()
        z_range = xyz_norm[:, 2].max() - xyz_norm[:, 2].min() + 1e-6
        xyz_norm[:, 2] = (xyz_norm[:, 2] - xyz_norm[:, 2].min()) / z_range

        # ── Process in chunks ────────────────────────────────────────────
        all_probs = np.zeros(N, dtype=np.float32)
        rng       = np.random.default_rng(42)

        n_chunks  = (N + self.chunk_size - 1) // self.chunk_size
        for i in range(n_chunks):
            # Random sampling per chunk (matches training DataLoader behaviour)
            if N > self.chunk_size:
                idx = rng.choice(N, self.chunk_size, replace=False)
            else:
                idx = np.arange(N)

            chunk_probs       = self._predict_chunk(xyz_norm[idx])
            all_probs[idx]    = np.maximum(all_probs[idx], chunk_probs)

            if (i + 1) % 10 == 0 or (i + 1) == n_chunks:
                logger.info(f"  Chunk {i+1}/{n_chunks} …")

        # ── Apply threshold ──────────────────────────────────────────────
        ground_mask   = all_probs >= self.threshold
        ground_points = points[ground_mask]

        pct = len(ground_points) / N * 100
        logger.info(
            f"  AI classification done: {len(ground_points):,} ground "
            f"({pct:.1f}%) of {N:,} total — threshold={self.threshold:.3f}"
        )

        if len(ground_points) < 100:
            logger.warning(
                "Very few ground points found by AI classifier! "
                "Check that:\n"
                "  1. The model file matches the architecture in this module.\n"
                "  2. The threshold is not too high (try lowering it to 0.3–0.4).\n"
                "  3. Your point cloud is not heavily unclassified noise."
            )

        return ground_points

    def extract_with_stats(self, points: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Same as extract() but also returns classification statistics.

        Returns:
            ground_points: (M, 3) XYZ array.
            stats: dict with keys total_points, ground_points, ground_pct,
                   threshold, device.
        """
        ground = self.extract(points)
        stats  = {
            "total_points":  len(points),
            "ground_points": len(ground),
            "ground_pct":    round(len(ground) / max(len(points), 1) * 100, 2),
            "threshold":     self.threshold,
            "device":        str(self.device),
            "chunk_size":    self.chunk_size,
        }
        return ground, stats
