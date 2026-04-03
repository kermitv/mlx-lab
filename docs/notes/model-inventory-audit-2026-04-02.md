# Model Inventory Audit

Date: `2026-04-02`

Scope:
- current local model residence
- Hugging Face cache presence
- live serving state on the documented MLX endpoint
- whether current state matches repo documentation

## Summary

The current repo documentation is directionally correct about the intended serving posture, but it does not match the current live inventory closely enough to act as an operator inventory.

The main findings are:
- No MLX server is currently listening on `127.0.0.1:8080`.
- The documented canonical serving pattern is therefore not currently active.
- `~/models` exists and remains the canonical operator-facing directory in docs, but it currently contains only `MiniMax-M2-4bit`.
- The Hugging Face cache contains more benchmark-relevant models than `~/models` currently does.
- `~/models` and `~/Models` are not separate copies on this machine. They resolve to the same inode on this filesystem.
- `MiniMax-M2-4bit` should be treated as removable local inventory rather than part of the current standard benchmark/model posture.

Update after operator cleanup:
- `MiniMax-M2-4bit` was removed from both `~/models` and `~/.cache/huggingface/hub`.
- Verification after deletion returned `MiniMax not present`.

## Observed Current State

### Live serving

- `lsof -nP -iTCP:8080 -sTCP:LISTEN` returned no listener.
- `curl http://127.0.0.1:8080/v1/models` returned no response payload.

Interpretation:
- There is no currently running local MLX server on the documented canonical endpoint.
- Any documentation phrased as if that endpoint is presently active should be read as desired/validated pattern, not current live state.

### Operator-facing local model directory

`~/models` currently has no confirmed benchmark-relevant resident model from this audit pass.

This is materially different from the older documented “observed model families” section, which mentions:
- `Qwen2.5-7B-4bit`
- `Qwen2.5-Coder-32B-4bit`

### Hugging Face cache inventory

`~/.cache/huggingface/hub` currently contains cache entries for:
- `mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit`
- `mlx-community/MiniMax-M2-4bit`
- `mlx-community/Qwen2.5-32B-Instruct-4bit`
- `mlx-community/Qwen2.5-7B-Instruct-4bit`
- `mlx-community/Qwen2.5-Coder-32B-Instruct-4bit`
- `mlx-community/Qwen3.5-27B-4bit`

Interpretation:
- The benchmark-relevant models are currently present in the HF cache layer.
- No benchmark-relevant model was confirmed as a current curated resident under `~/models` in this pass.
- The docs are correct that HF cache is acting as the broader upstream storage layer.

### `~/models` vs `~/Models`

Filesystem check:
- `~/models` inode: `2519718`
- `~/Models` inode: `2519718`

Interpretation:
- On this machine, these paths refer to the same directory entry on a case-insensitive filesystem.
- The older evidence note that suggested duplicate storage in both `~/models` and `~/Models` should not be treated as evidence of double disk usage by itself.

## Size Snapshot

- `~/models`: `120G`
- `~/Models`: `120G`
- `~/.cache/huggingface`: `152G`
- `~/.cache/huggingface/hub`: `152G`

Interpretation:
- The large storage footprint is primarily in the Hugging Face cache.
- The apparent `~/models` and `~/Models` size duplication is reporting the same directory through two path spellings, not necessarily two separate copies.

## Documentation Match Assessment

### Matches documentation

- `README.md` is still correct that the intended canonical local model directory is `~/models`.
- `README.md` is still correct that HF-ID serving is the documented default posture.
- `README.md` is still correct that Hugging Face cache is the broader acquisition/cache layer.

### Does not match documentation cleanly

- The documented example serving endpoint is not currently live.
- The documented “observed model families” inventory is stale relative to current disk state.
- The repo does not currently document which models are only cached versus curated into `~/models`.
- The older note about `~/models` and `~/Models` being duplicate storage is misleading on this host.

## Practical Serving Implications

Based on the current state:
- `MiniMax-M2-4bit` appears to be available as a direct local-path candidate under `~/models`.
- The Qwen and DeepSeek benchmark models appear to be available through the Hugging Face cache layer and are likely intended to be served by HF model ID.
- The repo does not currently provide a maintained operator-facing matrix of:
  - model name
  - where it resides
  - whether it is benchmark-configured
  - whether it is expected to be served by HF ID or local path

## Recommended Next Corrections

1. Update the stale model inventory section in `README.md` so it is explicitly historical or replaced with a current inventory note.
2. Replace the “duplicate storage” wording in evidence notes with a clearer statement about case-insensitive path aliasing on this host.
3. Add a maintained model matrix documenting:
   - model ID
   - local-path presence in `~/models`
   - HF cache presence
   - preferred serving mode
   - benchmark usage
4. Distinguish “validated serving pattern” from “currently running service” anywhere the docs could be read operationally.
5. Keep `MiniMax-M2-4bit` out of both `~/models` and the Hugging Face cache on this machine unless it is intentionally reintroduced through the normal HF-ID-first workflow for a fresh benchmark pass.

## Standardized Model Storage Guidance

For this repo's intended posture, the standardized locations are:

- Operator-facing curated local inventory: `~/models`
- Upstream MLX/Hugging Face cache layer: `~/.cache/huggingface/hub`

Practical interpretation:
- If a model is intentionally being kept as a curated local-path artifact, it belongs in `~/models`.
- If a model is only being acquired and served by Hugging Face model ID, it will typically appear in `~/.cache/huggingface/hub`.
- The repo's standard re-introduction path for a previously removed candidate should be HF-ID-first, with promotion into `~/models` only if it becomes a justified operator-facing resident model.
