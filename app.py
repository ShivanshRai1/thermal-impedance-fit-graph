from __future__ import annotations

import json
from typing import Any

from flask import Flask, Response, jsonify, render_template, request

from fit_plot import (
    compute_curves,
    parse_number_list,
    render_overlay_png_base64,
    render_overlay_png_bytes,
)


app = Flask(__name__)


def _build_curves_from_mapping(values: Any) -> Any:
    tp = parse_number_list(values.get("tp", ""))
    zth = parse_number_list(values.get("zth", ""))
    foster_r = parse_number_list(values.get("foster_r", ""))
    foster_c = parse_number_list(values.get("foster_c", ""))
    cauer_r = parse_number_list(values.get("cauer_r", ""))
    cauer_c = parse_number_list(values.get("cauer_c", ""))
    order = int(values.get("order", 1))

    curves = compute_curves(
        tp_actual=tp,
        zth_actual=zth,
        foster_r=foster_r,
        foster_c=foster_c,
        cauer_r=cauer_r,
        cauer_c=cauer_c,
        order=order,
    )
    return curves, order


def _curves_to_dict(curves: Any, order: int) -> dict[str, Any]:
    return {
        "order_used": int(order),
        "tp_actual": [float(v) for v in curves.tp_actual.tolist()],
        "zth_actual": [float(v) for v in curves.zth_actual.tolist()],
        "tp_grid": [float(v) for v in curves.tp_grid.tolist()],
        "zth_foster": [float(v) for v in curves.zth_foster.tolist()],
        "zth_cauer": [float(v) for v in curves.zth_cauer.tolist()],
    }


@app.get("/")
def index() -> str:
    return render_template("index.html", prefill=None)


@app.post("/")
def index_post() -> str:
    payload = request.get_json(silent=True) or {}
    prefill = {
        "order": payload.get("order", 5),
        "tp": payload.get("tp", "1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1,3,10,30,100"),
        "zth": payload.get("zth", "0.01,0.03,0.06,0.10,0.16,0.23,0.31,0.38,0.44,0.49,0.53,0.56,0.58"),
        "foster_r": payload.get("foster_r", "0.05,0.12,0.14,0.15,0.12"),
        "foster_c": payload.get("foster_c", "0.002,0.02,0.2,2.0,20.0"),
        "cauer_r": payload.get("cauer_r", "0.02,0.08,0.15,0.18,0.15"),
        "cauer_c": payload.get("cauer_c", "0.01,0.04,0.22,1.8,16.0"),
    }
    return render_template("index.html", prefill=prefill)


@app.get("/zth-fit")
def zth_fit_page() -> str:
    return render_template("zth_fit.html")


@app.post("/plot")
def plot_overlay() -> Any:
    payload = request.get_json(silent=True) or {}

    try:
        curves, order = _build_curves_from_mapping(payload)
        png_b64 = render_overlay_png_base64(curves)

        return jsonify(
            {
                "image_base64": png_b64,
                "meta": {
                    "n_points_actual": int(curves.tp_actual.size),
                    "n_points_curve": int(curves.tp_grid.size),
                    "order_used": order,
                },
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/zth-fit.png")
def zth_fit_png() -> Any:
    try:
        curves, _ = _build_curves_from_mapping(request.args)
        png = render_overlay_png_bytes(curves)
        return Response(png, mimetype="image/png")
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/zth-overlay.png", methods=["GET", "POST"])
def zth_overlay_png_api() -> Any:
    try:
        values = request.args if request.method == "GET" else (request.get_json(silent=True) or {})
        curves, _ = _build_curves_from_mapping(values)
        png = render_overlay_png_bytes(curves)
        return Response(png, mimetype="image/png")
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/zth-overlay-data", methods=["GET", "POST"])
def zth_overlay_data_api() -> Any:
    try:
        values = request.args if request.method == "GET" else (request.get_json(silent=True) or {})
        curves, order = _build_curves_from_mapping(values)
        return jsonify(_curves_to_dict(curves, order))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/zth-overlay", methods=["GET", "POST"])
def zth_overlay_interactive_api() -> Any:
    try:
        values = request.args if request.method == "GET" else (request.get_json(silent=True) or {})
        curves, order = _build_curves_from_mapping(values)
        payload = _curves_to_dict(curves, order)
        return render_template("zth_overlay_interactive.html", payload_json=json.dumps(payload))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
