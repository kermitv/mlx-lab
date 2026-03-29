# Evidence — MLX Lab

This folder contains point-in-time captures of the MLX environment on oc-mac-m5.

These are:
- read-only snapshots
- used for analysis and comparison
- not treated as canonical configuration

---

## 2026-03-29 — Phase 1 Capture

Path:
evidence/oc-mac-m5-mlx-phase1-20260329-121148/

Purpose:
Initial interrogation of MLX environment.

Captured:
- Python environments
- MLX packages
- running processes
- model inventory
- cache locations
- ports and endpoints
- OpenClaw config (redacted)

Notes:
- Multiple MLX envs detected (~/.mlx-venv, ~/mlx-env)
- MLX server running on port 8080
- Bound to 0.0.0.0 (not loopback-only)
- Duplicate model storage observed (~/models, ~/Models, HF cache)

