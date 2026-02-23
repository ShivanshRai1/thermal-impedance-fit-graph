from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from thermal_network.conversions import cauer_to_foster
from thermal_network.impedance import foster_impedance_time_domain
from thermal_network.networks import CauerNetwork, FosterNetwork


@dataclass
class CurveBundle:
    tp_actual: np.ndarray
    zth_actual: np.ndarray
    tp_grid: np.ndarray
    zth_foster: np.ndarray
    zth_cauer: np.ndarray


def parse_number_list(raw: str | Iterable[float]) -> np.ndarray:
    if isinstance(raw, str):
        cleaned = raw.replace("\n", ",").replace(";", ",").replace("\t", ",")
        parts = [p.strip() for p in cleaned.split(",") if p.strip()]
        arr = np.asarray([float(p) for p in parts], dtype=float)
    else:
        arr = np.asarray(list(raw), dtype=float)

    if arr.ndim != 1 or arr.size == 0:
        raise ValueError("Expected a non-empty 1D numeric list.")
    if not np.all(np.isfinite(arr)):
        raise ValueError("Input contains non-finite values.")
    return arr


def _validate_order(order: int, r: np.ndarray, c: np.ndarray, label: str) -> tuple[np.ndarray, np.ndarray]:
    if order < 1:
        raise ValueError("order must be >= 1")
    if len(r) < order or len(c) < order:
        raise ValueError(f"{label} r/c must have at least 'order' elements.")
    return r[:order], c[:order]


def compute_curves(
    tp_actual: np.ndarray,
    zth_actual: np.ndarray,
    foster_r: np.ndarray,
    foster_c: np.ndarray,
    cauer_r: np.ndarray,
    cauer_c: np.ndarray,
    order: int,
    n_grid: int = 450,
) -> CurveBundle:
    tp = np.asarray(tp_actual, dtype=float)
    zth = np.asarray(zth_actual, dtype=float)

    if tp.shape != zth.shape:
        raise ValueError("tp and zth must have same length.")
    if np.any(tp <= 0):
        raise ValueError("All tp values must be > 0 for log-scale plotting.")

    idx = np.argsort(tp)
    tp = tp[idx]
    zth = zth[idx]

    foster_r, foster_c = _validate_order(order, np.asarray(foster_r, dtype=float), np.asarray(foster_c, dtype=float), "Foster")
    cauer_r, cauer_c = _validate_order(order, np.asarray(cauer_r, dtype=float), np.asarray(cauer_c, dtype=float), "Cauer")

    if np.any(foster_r <= 0) or np.any(foster_c <= 0):
        raise ValueError("Foster R/C values must be positive.")
    if np.any(cauer_r <= 0) or np.any(cauer_c <= 0):
        raise ValueError("Cauer R/C values must be positive.")

    tmin = float(np.min(tp))
    tmax = float(np.max(tp))
    if tmin == tmax:
        tmin = max(tmin / 10.0, 1e-12)
        tmax = tmax * 10.0

    tp_grid = np.logspace(np.log10(tmin), np.log10(tmax), int(n_grid))

    foster_net = FosterNetwork(r=foster_r, c=foster_c)
    zth_foster = foster_impedance_time_domain(foster_net, tp_grid)

    cauer_net = CauerNetwork(r=cauer_r, c=cauer_c)
    cauer_as_foster = cauer_to_foster(cauer_net)
    zth_cauer = foster_impedance_time_domain(cauer_as_foster, tp_grid)

    return CurveBundle(
        tp_actual=tp,
        zth_actual=zth,
        tp_grid=tp_grid,
        zth_foster=np.asarray(zth_foster, dtype=float),
        zth_cauer=np.asarray(zth_cauer, dtype=float),
    )


def render_overlay_png_base64(curves: CurveBundle) -> str:
    return base64.b64encode(render_overlay_png_bytes(curves)).decode("ascii")


def render_overlay_png_bytes(curves: CurveBundle) -> bytes:
    fig, ax = plt.subplots(figsize=(8.4, 5.0), dpi=150)

    ax.scatter(
        curves.tp_actual,
        curves.zth_actual,
        s=20,
        color="#0f172a",
        alpha=0.85,
        label="Digitized Zth points (actual)",
        zorder=3,
    )
    ax.plot(
        curves.tp_grid,
        curves.zth_foster,
        color="#2563eb",
        linewidth=2.1,
        alpha=0.8,
        label="Foster fit curve",
        zorder=2,
    )
    ax.plot(
        curves.tp_grid,
        curves.zth_cauer,
        color="#dc2626",
        linewidth=2.6,
        linestyle=(0, (5, 3)),
        label="Cauer fit curve",
        zorder=4,
    )

    ax.set_xscale("log")
    ax.set_xlabel("tp (s)")
    ax.set_ylabel("Zth (K/W)")
    ax.set_title("Zth vs tp: Actual vs Foster/Cauer Fits")
    ax.grid(which="both", linestyle=":", linewidth=0.7, alpha=0.55)
    ax.legend(loc="best", frameon=True)

    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    return buffer.getvalue()
