# Thermal Impedance Fit Graphs - How To Run

## Python Version Requirement

- Use Python `3.11` (or at least `3.10`).
- Python `3.9` is not supported for this project because one dependency (`jax`, pulled by `thermal-network`) uses Python 3.10+ syntax.

## Setup

```bash
cd "Thermal impedance fit graphs"
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Wait until you see:

- `Running on http://127.0.0.1:5001`

Then keep that terminal open and open the links below.

## If You Already Created a Python 3.9 venv

Recreate it with Python 3.11:

```bash
cd "Thermal impedance fit graphs"
deactivate 2>/dev/null || true
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

## Shell Note

If you paste a line starting with `#` and see `zsh: command not found: #`, remove that line and run only the actual commands.

Open:

- `http://127.0.0.1:5001/` - Main interactive app page (form input + generated plot view).
- `http://127.0.0.1:5001/zth-fit` - URL endpoint reference page with sample links.
- `http://127.0.0.1:5001/api/zth-overlay?order=5&tp=1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1,3,10,30,100&zth=0.01,0.03,0.06,0.10,0.16,0.23,0.31,0.38,0.44,0.49,0.53,0.56,0.58&foster_r=0.05,0.12,0.14,0.15,0.12&foster_c=0.002,0.02,0.2,2.0,20.0&cauer_r=0.02,0.08,0.15,0.18,0.15&cauer_c=0.01,0.04,0.22,1.8,16.0` - Interactive graph-only page (hover/zoom/pan), ideal for iframe embedding.
- `http://127.0.0.1:5001/api/zth-overlay-data?order=5&tp=1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1,3,10,30,100&zth=0.01,0.03,0.06,0.10,0.16,0.23,0.31,0.38,0.44,0.49,0.53,0.56,0.58&foster_r=0.05,0.12,0.14,0.15,0.12&foster_c=0.002,0.02,0.2,2.0,20.0&cauer_r=0.02,0.08,0.15,0.18,0.15&cauer_c=0.01,0.04,0.22,1.8,16.0` - JSON data endpoint (actual points + Foster/Cauer curve arrays) for custom frontend charts.
- `http://127.0.0.1:5001/api/zth-overlay.png?order=5&tp=1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1,3,10,30,100&zth=0.01,0.03,0.06,0.10,0.16,0.23,0.31,0.38,0.44,0.49,0.53,0.56,0.58&foster_r=0.05,0.12,0.14,0.15,0.12&foster_c=0.002,0.02,0.2,2.0,20.0&cauer_r=0.02,0.08,0.15,0.18,0.15&cauer_c=0.01,0.04,0.22,1.8,16.0` - PNG image endpoint (non-interactive) for quick previews/export.
- `http://127.0.0.1:5001/zth-fit.png?order=5&tp=1e-4,3e-4,1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1,3,10,30,100&zth=0.01,0.03,0.06,0.10,0.16,0.23,0.31,0.38,0.44,0.49,0.53,0.56,0.58&foster_r=0.05,0.12,0.14,0.15,0.12&foster_c=0.002,0.02,0.2,2.0,20.0&cauer_r=0.02,0.08,0.15,0.18,0.15&cauer_c=0.01,0.04,0.22,1.8,16.0` - Legacy direct PNG route (same behavior as `/api/zth-overlay.png`).

## Input Expectations

- `tp`: digitized time points (> 0), comma/newline/semicolon separated
- `zth`: digitized thermal impedance points, same length as `tp`
- Foster and Cauer `R`/`C` lists: at least `N` values each
- `Order N`: the first `N` values of each `R`/`C` list are used

The generated plot overlays:

1. Digitized actual points (scatter)
2. Foster fit curve (solid)
3. Cauer fit curve (dashed)

All on the same `Zth vs tp` axes with logarithmic `tp` scale.

## URL Endpoint Parameters

- `order`: positive integer
- `tp`, `zth`: same-length numeric lists
- `foster_r`, `foster_c`: positive lists with at least `order` values
- `cauer_r`, `cauer_c`: positive lists with at least `order` values
- Interactive graph page for embedding (hover/zoom): `GET /api/zth-overlay?...` (also accepts `POST` JSON with same fields)
- Raw graph data for custom frontend charting: `GET/POST /api/zth-overlay-data`
- PNG fallback (non-interactive): `GET/POST /api/zth-overlay.png`

### UI Embed Example (Interactive)

```html
<iframe
  src="http://127.0.0.1:5001/api/zth-overlay?order=5&tp=...&zth=...&foster_r=...&foster_c=...&cauer_r=...&cauer_c=..."
  width="100%"
  height="680"
  style="border:0;border-radius:12px"
></iframe>
```

## References

- Thermal Network conversions: `https://thermal-network.pages.dev/reference/conversions/`
- Thermal Network impedance API: `https://thermal-network.pages.dev/reference/impedance/`
- Infineon thermal model overview: `https://community.infineon.com/t5/Knowledge-Base-Articles/Types-of-thermal-models-and-how-to-find-thermal-network-coefficients/ta-p/974861`
