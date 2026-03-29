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

## Model Source Strategy (working mental model)

MLX supports multiple ways of loading models:

- Hugging Face model IDs (e.g. `mlx-community/Qwen2.5-32B-Instruct-4bit`)
- Local model directories (paths on disk)
- Converted models produced via `mlx_lm.convert`

Hugging Face integration is the default behavior for MLX:
- Models are downloaded automatically when referenced
- Models are cached locally under `~/.cache/huggingface/hub`
- Tokenizers and configs are resolved automatically  [oai_citation:0‡Hugging Face](https://huggingface.co/docs/hub/en/mlx?utm_source=chatgpt.com)

The lab uses a layered model:

- Hugging Face cache (`~/.cache/huggingface`)
  - Role: upstream distribution and caching layer
  - Not operator-facing
  - Not considered the canonical model inventory

- Local model directory (candidate: `~/models`)
  - Role: curated, operator-visible model inventory
  - Intended future canonical reference for serving and documentation

Notes:
- MLX can load both Hugging Face IDs and local paths  [oai_citation:1‡GitHub](https://github.com/simonw/llm-mlx/issues/12?utm_source=chatgpt.com)
- Hugging Face is preferred for discovery and initial model acquisition
- Local directories will be used for clarity, reproducibility, and multi-client usage

Status:
- This is a working mental model only
- No cleanup, migration, or enforcement has been performed yet

Open questions:
- Should MLX server serve from Hugging Face IDs, local paths, or both?
- How should models be promoted from Hugging Face cache into local directory?
- Should duplicate local directories be consolidated or removed?

---

## Open Questions

---

## Next Actions
