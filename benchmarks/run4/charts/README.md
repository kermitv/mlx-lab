# Run 4 Charts

This chart set is generated from `benchmarks/run4/data/rows.csv` and `benchmarks/run4/data/routing_summary.json`.

Files:
- `quality_vs_latency.svg`: shows the quality/latency tradeoff by model and task.
- `task_model_heatmap.svg`: shows per-task accuracy across all models with finish-state badges.
- `frontier_vs_local_gap.svg`: shows how much frontier beats or trails the best local result by task class.
- `operational_vs_quality.svg`: shows which results are strongest as unattended defaults versus strongest by answer quality.

Notes:
- The environment did not have plotting libraries installed, so these charts are emitted as dependency-free SVGs.
- These visuals are presentation artifacts derived from the Run 4 data layer; they are not new benchmark evidence.
