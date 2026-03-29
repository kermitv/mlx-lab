# MLX Lab — oc-mac-m5

Purpose:
Stabilize MLX into a reproducible, high-performance local inference service
usable by multiple local clients and testable with OpenClaw.

Node posture:
- oc-mac-m5 = validation/buildout
- local-first, loopback-first
- optional tier-2 only

---

## Current Known Facts

(To be filled in from Phase 1)

---

## Evidence

Initial MLX environment capture (Phase 1):

- Path:
  `evidence/oc-mac-m5-mlx-phase1-20260329-121148/`

- Purpose:
  Point-in-time snapshot of MLX environment on oc-mac-m5 for analysis.

- Captured via:
  `scripts/phase1-capture.sh`

- Contains:
  - Python environments
  - MLX packages
  - running processes
  - model inventory
  - cache locations
  - ports and endpoints
  - OpenClaw config (redacted)

Notes:
- Multiple MLX environments detected (`~/.mlx-venv`, `~/mlx-env`)
- MLX server currently running on port `8080`
- Server bound to `0.0.0.0` (not loopback-only)
- Duplicate model storage exists (`~/models`, `~/Models`, Hugging Face cache)

---

## Decisions (only after validated)

### Canonical MLX environment candidate

Selected candidate: `~/mlx-env`

Why:
- This environment has the clearest verified MLX package set in the Phase 1 evidence.
- It appears to be the best operator-facing MLX environment for serving, benchmarking, and local client reuse.
- It is less entangled with OpenClaw application/runtime work than `~/Projects/OpenClaw/venv`.
- Local client use against the MLX endpoint has already been exercised from this environment.

Not selected for now:
- `~/.mlx-venv` — retained temporarily for comparison/rollback only because it is the currently serving MLX environment on port `8080`.
- `~/Projects/OpenClaw/venv` — retained as an application-specific project environment, not the canonical MLX environment.

---

## Commands That Actually Work

---

## Open Questions

---

## Next Actions
