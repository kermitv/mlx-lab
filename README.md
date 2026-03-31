# MLX Lab — oc-mac-m5

Purpose:
Stabilize MLX into a reproducible, high-performance local inference service
usable by multiple local clients and testable with OpenClaw.

Node posture:
- oc-mac-m5 = validation/buildout
- local-first, loopback-first
- optional tier-2 only

---

## Benchmark Program

The benchmark work in this repo has become a small routing study, not just a speed test.

Run progression so far:
- Run 1 established baseline local viability and showed that the fast 7B lane was already useful on this node.
- Run 2 shifted from “one best model” toward “best model by use case,” separating operational default, reasoning, and coding roles.
- Run 3 sharpened local escalation thresholds by task class, even though frontier access was unavailable in that run.
- Run 4 tested the local-to-frontier escalation boundary directly and confirmed the current mlx-lab routing story:
  - fast local default: `mlx-community/Qwen2.5-7B-Instruct-4bit`
  - local coding specialist: `mlx-community/Qwen2.5-Coder-32B-Instruct-4bit`
  - local reasoning/governance lane: `mlx-community/Qwen2.5-32B-Instruct-4bit`
  - frontier produced stronger answers on some tasks, but did not justify universal escalation in this run

Presentation-oriented Run 4 review:
- Dashboard:
  [`benchmarks/run4/index.html`](benchmarks/run4/index.html) — presentation-oriented review surface with charts, narrative framing, and links into the underlying Run 4 data.
- Normalized data:
  `benchmarks/run4/data/`
- Full Run 4 execution evidence:
  `benchmark-runs/run-20260329-run4-frontier-boundary/`

Current benchmark posture:
- useful for mlx-lab routing guidance now
- still bounded to this host, this model set, and these benchmark families
- not yet promotion-grade evidence for canonical OpenClaw runtime policy

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
- This capture reflects the earlier observed state before cleanup and standardization.
- It remains useful as baseline evidence, but current validated decisions are recorded below.

---

## Decisions (only after validated)

### Canonical MLX environment

Selected: `~/mlx-env`

Why:
- This environment has the clearest verified MLX package set in the Phase 1 evidence.
- It appears to be the best operator-facing MLX environment for serving, benchmarking, and local client reuse.
- It is less entangled with OpenClaw application/runtime work than `~/Projects/OpenClaw/venv`.
- Local client use against the MLX endpoint has already been exercised from this environment.

Not selected:
- `~/Projects/OpenClaw/venv` — application-specific project environment, not the canonical MLX environment

### Canonical local model directory

Selected: `~/models`

Why:
- Simpler and more conventional lowercase path for operator-facing documentation
- Better fit for a curated local model inventory concept
- Easier to reference consistently across lab notes and local client examples

Not selected:
- `~/.cache/huggingface/hub` — upstream cache layer, not the canonical local model directory

### Local model inventory

Observed model families:
- `Qwen2.5-7B-4bit`
- `Qwen2.5-Coder-32B-4bit`

Observed sizes:
- `Qwen2.5-7B-4bit` ≈ `4.0G`
- `Qwen2.5-Coder-32B-4bit` ≈ `17G`

Current state:
- `~/models` is the canonical local model directory
- Current validated default serving pattern still uses Hugging Face model IDs, not local paths
- Local-path serving from `~/models` remains a validated controlled option

### Local-path serving validation (7B model)

Validated command:
    source ~/mlx-env/bin/activate
    python -m mlx_lm server \
      --model ~/models/Qwen2.5-7B-4bit \
      --port 8080 \
      --host 127.0.0.1

Validation results:
- server started successfully from explicit local path
- `/health` returned `{"status": "ok"}`
- `/v1/models` returned the local-path model entry
- `/v1/chat/completions` succeeded

Observed model ID:
- `/Users/kermitv/models/Qwen2.5-7B-4bit`

Observed tradeoff:
- local-path serving gives stronger control over exact artifacts
- Hugging Face ID serving remains cleaner for client ergonomics
- recommended current default remains HF-ID serving
- local-path serving is now a validated controlled option

### Default serving style decision

Selected default:
- Hugging Face ID serving

Validated controlled option:
- local-path serving from `~/models`

Why this default:
- Cleaner model identifiers for local clients
- Better client ergonomics for OpenAI-compatible tools
- Still uses local cached artifacts in practice
- Keeps explicit local-path serving available when tighter artifact control is needed

Current implication:
- Canonical day-to-day server usage remains HF-ID based
- Local-path serving is retained as a documented and validated option, not the default

### Canonical MLX server launch pattern (validated)

Environment: `~/mlx-env`
Port: `8080`
API shape: OpenAI-compatible `/v1`
Bind target: `127.0.0.1`
Default model reference style: Hugging Face model ID

Command:
```bash
source ~/mlx-env/bin/activate
python -m mlx_lm server \
  --model mlx-community/Qwen2.5-32B-Instruct-4bit \
  --port 8080 \
  --host 127.0.0.1
```

Why:
- Matches the currently working OpenAI-compatible MLX API pattern already observed on port `8080`
- Keeps local client configuration simple and consistent
- Preserves Hugging Face as the upstream integration path while local model inventory is still being clarified
- Fits the local-first / loopback-first intended posture for this lab

Validation evidence:
- Server successfully started from `~/mlx-env`
- `/health` endpoint returned `{"status": "ok"}`
- `/v1/models` returned model list
- Aider successfully connected using OpenAI-compatible API
- No dependency on `~/.mlx-venv`

Current live variance:
- Earlier observed server state used a different environment and broader bind target
- Canonical pattern now uses `~/mlx-env` and `127.0.0.1`

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

- Local model directory (`~/models`)
  - Role: curated, operator-visible model inventory
  - Canonical local model directory for operator-facing documentation

Notes:
- MLX can load both Hugging Face IDs and local paths  [oai_citation:1‡GitHub](https://github.com/simonw/llm-mlx/issues/12?utm_source=chatgpt.com)
- Hugging Face is preferred for discovery and initial model acquisition
- Local directories will be used for clarity, reproducibility, and multi-client usage

Status:
- This is still a working mental model around sourcing and promotion
- Current validated default remains HF-ID serving with local-path serving as a controlled option

Open questions:
- Should MLX server serve from Hugging Face IDs, local paths, or both?
- How should models be promoted from Hugging Face cache into local directory?
- When should operator-facing docs prefer the canonical local model inventory over the Hugging Face cache view?

---

## Token Handling (current lab pattern)

Scope:
- Hugging Face token handling for MLX model acquisition on `oc-mac-m5`

Current pattern:
- Do not store `HF_TOKEN` in `~/.zprofile` or other always-loaded shell startup files
- Do not store tokens in this repo
- Prefer macOS Keychain for secure local storage
- Acceptable fallback: manual session export outside the repo when needed
- Cached local models may allow serving without an active Hugging Face token

Preferred handling:
- Store the token outside repo-tracked files
- Export it only when needed for new model acquisition or gated model access
- Treat shell history, dotfiles, logs, and markdown notes as places where secrets should not live

Status:
- This is the current MLX lab handling pattern only
- It is not yet a governed OpenClaw runtime procedure

Future promotion note:
- If Hugging Face token handling becomes part of the stable `oc-mac-m5` bring-up or governed runtime operating pattern, promote a compact no-secrets version of this guidance into `openclaw-runtime-lab`
- Any promoted version should keep secrets node-local and out of repos

## Phase Status

### Phase 1 — Baseline validation (complete)

- [x] Canonical MLX environment selected (`~/mlx-env`)
- [x] MLX server launch pattern defined and validated
- [x] Server bound to loopback (`127.0.0.1`)
- [x] OpenAI-compatible API confirmed (`/v1`)
- [x] `/health` endpoint returns OK
- [x] `/v1/models` returns expected models
- [x] At least one real client works (Aider)
- [x] Hugging Face token removed from shell config
- [x] Token stored in Keychain and retrievable
- [x] README reflects validated state only (no speculation)

### Phase 2 — Model control (complete)

- [x] Canonical model directory enforced (`~/models`)
- [x] HF cache vs local model inventory clarified
- [x] Optional: migrate one model to local-path serving
- [x] Remove or archive unused MLX environments

Done:
- `~/models` is canonical
- `~/Models` retired
- `~/.mlx-venv` retired
- `~/mlx-env` remains canonical
- HF-ID serving revalidated successfully
- local-path serving validated

---

## Next Actions

- Add a small GitHub Pages narrative surface for the benchmark program if the Run 4 dashboard proves useful for ongoing review
- Expand the benchmark series with repeated-run stability checks, better memory observability, and harder multi-file repair tasks
- Keep current mlx-lab routing guidance clearly separated from any future OpenClaw runtime-policy promotion
