# Run 4 Current State

This note is a retained working summary of Run 4 in `mlx-lab`. It reflects current benchmark evidence only and does not establish canonical routing policy outside this workspace.

## Run Completion

Run 4 completed at `2026-03-29 20:40:36 MDT` using the benchmark bundle captured under `benchmarks/run4/` and the full execution evidence kept locally under `benchmark-runs/run-20260329-run4-frontier-boundary/`.

## Benchmarked Models

Local models:
- `mlx-community/Qwen2.5-7B-Instruct-4bit`
- `mlx-community/Qwen2.5-Coder-32B-Instruct-4bit`
- `mlx-community/Qwen3.5-27B-4bit`
- `mlx-community/Qwen2.5-32B-Instruct-4bit`

Frontier models:
- `gpt-5.2-codex`
- `gpt-5.4`

## Current Best-Of Findings

- Best local operational default: `mlx-community/Qwen2.5-7B-Instruct-4bit`
- Best local coding model: `mlx-community/Qwen2.5-Coder-32B-Instruct-4bit`
- Best local reasoning/governance model: `mlx-community/Qwen2.5-32B-Instruct-4bit`
- Frontier result: `gpt-5.4` achieved the strongest quality in this run, but did not materially outperform the best local model under the run's materiality threshold because the gap stayed below `1.0` quality point.

## Routing Interpretation

- Keep the fast local default for routine bounded drafting, artifact checks, and low-risk single-hop tasks.
- Escalate to the stronger local coding lane for multi-file engineering repair and bounded code-generation work.
- Escalate to the stronger local reasoning lane for contradiction analysis, partial-failure reconstruction, and governance-sensitive synthesis inside `mlx-lab`.
- Escalate to frontier for ambiguous high-stakes tasks, promotion-grade governance decisions, or cases where local answers miss required evidence boundaries on the first pass.

## Memory Conclusion

For the current tested workload, memory appears satisfactory and is not an active bottleneck. Run 4 did not capture reliable per-process RSS or memory-percent telemetry because sandboxed `ps` and `top` snapshots were blocked, so this conclusion is based on successful execution plus operator observation rather than precise process-memory measurements.

## Evidence Limits

- Findings are bounded to this host, this MLX-served local endpoint, these model variants, and these benchmark families.
- The benchmark captured stronger latency and answer-quality evidence than memory-usage evidence.
- The frontier lane required governed API-shape handling for `gpt-5.2-codex` and bounded retries for `gpt-5.4` when initial responses exhausted output budget without visible answer text.
- These findings are directional and workspace-scoped, not promotion-grade runtime policy evidence.

## Likely Next Directions

- Add a memory-focused benchmark pass with real per-process memory sampling outside the current sandbox limitations.
- Stress larger local models, larger contexts, and multi-model concurrency to determine when RAM becomes the next real constraint.
- Repeat the routing benchmark across more task families to see whether the current local-vs-frontier boundary remains stable.
