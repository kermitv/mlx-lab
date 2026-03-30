Benchmark family 4 task:

Using prior benchmark evidence and current run results, answer:
- when to use fast local default
- when to use a stronger local coding specialist
- when to use a stronger local reasoning lane
- when to escalate to frontier
- what conclusions are mlx-lab-only
- what evidence is still missing before promotion into openclaw-runtime-lab

Require:
- routing by task class, not one universal winner
- explicit distinction between local guidance and promotion-grade evidence
- no overclaiming of topology or routing changes
- practical task-threshold recommendations

Prior run evidence:

[run3 quality_scores.csv]
```csv
model,multi_file_repair_quality_score_10,repo_engineering_quality_score_10,debugging_quality_score_10,escalation_decision_quality_score_10,overall_quality_score_10,notes
mlx-community/Qwen2.5-7B-Instruct-4bit,10.0,10.0,10.0,8.75,9.69,"multi_file_repair: finds mislabeled wall time, finds warm-up scoring defect, finds blocked-task omission; repo_engineering: checks both csv files, checks blocked tasks reflected in summary, clear exit codes; debugging: identifies contradictions, notes malformed reasoning log, notes blocked row vs success claim; escalation_decision: routes by task class, fast default threshold, coder 32b threshold"
mlx-community/Qwen2.5-Coder-32B-Instruct-4bit,8.75,10.0,7.5,8.75,8.75,"multi_file_repair: finds warm-up scoring defect, finds blocked-task omission, finds malformed json row loss; repo_engineering: checks both csv files, checks blocked tasks reflected in summary, clear exit codes; debugging: identifies contradictions, notes malformed reasoning log, notes blocked row vs success claim; escalation_decision: routes by task class, fast default threshold, coder 32b threshold"
mlx-community/Qwen2.5-32B-Instruct-4bit,8.75,10.0,8.75,8.75,9.06,"multi_file_repair: finds warm-up scoring defect, finds blocked-task omission, finds malformed json row loss; repo_engineering: checks both csv files, checks blocked tasks reflected in summary, clear exit codes; debugging: identifies contradictions, notes malformed reasoning log, notes blocked row vs success claim; escalation_decision: fast default threshold, coder 32b threshold, 32b instruct threshold"
gpt-5.2,0.0,0.0,0.0,0.0,0.0,multi_file_repair: blocked; repo_engineering: blocked; debugging: blocked; escalation_decision: blocked
gpt-5.4-mini,0.0,0.0,0.0,0.0,0.0,multi_file_repair: blocked; repo_engineering: blocked; debugging: blocked; escalation_decision: blocked
gpt-5.4,0.0,0.0,0.0,0.0,0.0,multi_file_repair: blocked; repo_engineering: blocked; debugging: blocked; escalation_decision: blocked
```

[run3 operational_scores.csv]
```csv
model,multi_file_repair_operational_score_10,repo_engineering_operational_score_10,debugging_operational_score_10,escalation_decision_operational_score_10,overall_operational_score_10,retries_used,human_rescue_required,notes
mlx-community/Qwen2.5-7B-Instruct-4bit,9.8,9.9,9.5,9.89,9.77,0,no,"multi_file_repair: non-empty answer, clean stop, no retry; repo_engineering: non-empty answer, clean stop, no retry; debugging: non-empty answer, clean stop, no retry; escalation_decision: non-empty answer, clean stop, no retry"
mlx-community/Qwen2.5-Coder-32B-Instruct-4bit,6.73,6.76,6.73,6.72,6.73,0,no,"multi_file_repair: non-empty answer, clean stop, no retry; repo_engineering: non-empty answer, clean stop, no retry; debugging: non-empty answer, clean stop, no retry; escalation_decision: non-empty answer, clean stop, no retry"
mlx-community/Qwen2.5-32B-Instruct-4bit,6.74,6.74,6.72,7.2,6.85,0,no,"multi_file_repair: non-empty answer, clean stop, no retry; repo_engineering: non-empty answer, clean stop, no retry; debugging: non-empty answer, clean stop, no retry; escalation_decision: non-empty answer, clean stop, no retry"
gpt-5.2,0.0,0.0,0.0,0.0,0.0,0,no,multi_file_repair: blocked; repo_engineering: blocked; debugging: blocked; escalation_decision: blocked
gpt-5.4-mini,0.0,0.0,0.0,0.0,0.0,0,no,multi_file_repair: blocked; repo_engineering: blocked; debugging: blocked; escalation_decision: blocked
gpt-5.4,0.0,0.0,0.0,0.0,0.0,0,no,multi_file_repair: blocked; repo_engineering: blocked; debugging: blocked; escalation_decision: blocked
```

Current run evidence so far:
```markdown
Model: gpt-5.2-codex
- benchmark-integrity-helper: quality=10.00 operational=9.00 blocked=False retries=0 note=both score csv checks, blocked tasks represented in summary, workspace boundary guard, clear exit codes, bounded practical implementation
- multi-file-repair: quality=9.00 operational=9.00 blocked=False retries=0 note=timing metric defect, warm-up scoring exclusion, blocked summary omission, malformed json row loss, bounded correction set
- partial-failure-debugging: quality=10.00 operational=10.00 blocked=False retries=0 note=contradictions identified, malformed log identified, likely sequence inferred, evidence preservation, correction vs history distinction, bounded correction set

Model: gpt-5.4
- benchmark-integrity-helper: quality=10.00 operational=8.25 blocked=False retries=1 note=both score csv checks, blocked tasks represented in summary, workspace boundary guard, clear exit codes, bounded practical implementation
- multi-file-repair: quality=10.00 operational=8.25 blocked=False retries=1 note=timing metric defect, warm-up scoring exclusion, blocked summary omission, malformed json row loss, bounded correction set, scoring exclusion rationale
- partial-failure-debugging: quality=10.00 operational=8.25 blocked=False retries=1 note=contradictions identified, malformed log identified, likely sequence inferred, evidence preservation, correction vs history distinction, bounded correction set

Model: mlx-community/Qwen2.5-32B-Instruct-4bit
- benchmark-integrity-helper: quality=10.00 operational=9.50 blocked=False retries=0 note=both score csv checks, blocked tasks represented in summary, workspace boundary guard, clear exit codes, bounded practical implementation
- multi-file-repair: quality=10.00 operational=8.75 blocked=False retries=0 note=timing metric defect, warm-up scoring exclusion, blocked summary omission, malformed json row loss, bounded correction set, scoring exclusion rationale
- partial-failure-debugging: quality=6.50 operational=9.50 blocked=False retries=0 note=contradictions identified, malformed log identified, likely sequence inferred, bounded correction set

Model: mlx-community/Qwen2.5-7B-Instruct-4bit
- benchmark-integrity-helper: quality=10.00 operational=9.50 blocked=False retries=0 note=both score csv checks, blocked tasks represented in summary, workspace boundary guard, clear exit codes, bounded practical implementation
- multi-file-repair: quality=9.00 operational=9.50 blocked=False retries=0 note=timing metric defect, warm-up scoring exclusion, blocked summary omission, malformed json row loss, bounded correction set
- partial-failure-debugging: quality=5.00 operational=9.50 blocked=False retries=0 note=contradictions identified, malformed log identified, bounded correction set

Model: mlx-community/Qwen2.5-Coder-32B-Instruct-4bit
- benchmark-integrity-helper: quality=10.00 operational=9.50 blocked=False retries=0 note=both score csv checks, blocked tasks represented in summary, workspace boundary guard, clear exit codes, bounded practical implementation
- multi-file-repair: quality=10.00 operational=8.75 blocked=False retries=0 note=timing metric defect, warm-up scoring exclusion, blocked summary omission, malformed json row loss, bounded correction set, scoring exclusion rationale
- partial-failure-debugging: quality=5.00 operational=9.50 blocked=False retries=0 note=contradictions identified, malformed log identified, bounded correction set

Model: mlx-community/Qwen3.5-27B-4bit
- benchmark-integrity-helper: quality=10.00 operational=7.75 blocked=False retries=0 note=both score csv checks, blocked tasks represented in summary, workspace boundary guard, clear exit codes, bounded practical implementation
- multi-file-repair: quality=9.00 operational=7.75 blocked=False retries=0 note=timing metric defect, warm-up scoring exclusion, blocked summary omission, malformed json row loss, bounded correction set
- partial-failure-debugging: quality=5.00 operational=8.75 blocked=False retries=0 note=contradictions identified, malformed log identified, bounded correction set
```
