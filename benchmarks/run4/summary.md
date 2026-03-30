# Run 4 Normalized Artifact

Source run: `/Users/kermitv/dev/mlx-lab/benchmark-runs/run-20260329-run4-frontier-boundary`
Record count: 24

## Layout
- `prompts/`: normalized copies of the task prompts.
- `raw/`: copied raw response payloads from the source run.
- `scored/`: one JSON record per model/task pair with the required fields.
- `summary.json`: full machine-readable bundle.

## Field Notes
- `score_accuracy` comes from the Run 4 per-task quality score.
- `score_structure` is a derived answer-shape score based on finish reason, retries, and completion cleanliness.
- `score_hallucination_risk` is a derived risk score where higher means more hallucination risk.

## Highest Accuracy Rows
- benchmark-integrity-helper | Qwen2.5-7B | accuracy 10.00 | latency 5.294s | structure 9.50 | hallucination_risk 2.50
- escalation-boundary-decision | Qwen2.5-7B | accuracy 10.00 | latency 7.934s | structure 9.50 | hallucination_risk 2.50
- benchmark-integrity-helper | gpt-5.2-codex | accuracy 10.00 | latency 9.244s | structure 7.50 | hallucination_risk 3.50
- partial-failure-debugging | gpt-5.2-codex | accuracy 10.00 | latency 9.588s | structure 9.50 | hallucination_risk 2.50
- benchmark-integrity-helper | Qwen2.5-Coder-32B | accuracy 10.00 | latency 18.422s | structure 9.50 | hallucination_risk 2.50
- benchmark-integrity-helper | Qwen2.5-32B | accuracy 10.00 | latency 19.975s | structure 9.50 | hallucination_risk 2.50
- multi-file-repair | Qwen2.5-32B | accuracy 10.00 | latency 28.143s | structure 9.50 | hallucination_risk 2.50
- partial-failure-debugging | gpt-5.4 | accuracy 10.00 | latency 30.203s | structure 8.25 | hallucination_risk 3.00
