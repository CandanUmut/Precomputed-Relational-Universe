
# PRU Additions v0.1 — Benchmarks + LaTeX Thesis

This package adds:
- **thesis/** — a LaTeX paper: *Precomputed Relational Universe (PRU): Dual-Lock Gravity and Relational Coherence*.
- **benchmarks/** — reproducible, tiny demos:
  - `chsh/` — Computes a CHSH value ~2.82 using quantum-consistent correlations.
  - `qft/` — Verifies a unitary QFT vs NumPy's FFT and reports L2 error + timing.
  - `lensing/` — Weak-field deflection for a point mass and CSV of (b, theta).
  - `superconducting/` — Toy Josephson-like double-well and numerical eigenlevels.

> Single-command runs:
```
python benchmarks/chsh/run.py
python benchmarks/qft/run.py
python benchmarks/lensing/run.py
python benchmarks/superconducting/run.py
```

**Notes**
- The CHSH demo produces outcome statistics with the **quantum correlation** \(E=-\cos(\Delta\theta)\) to reach S≈2.828; it is *not* a local hidden-variable model (by design).
- The superconducting demo is a **toy** (1D finite-difference Schrödinger in a Josephson-like potential) to illustrate level quantization; it is not a full transmon simulator.
- Requirements: see `requirements.txt` (NumPy, SciPy, Matplotlib).

Generated on: 2025-10-12T17:50:41.781464Z
