Benchmark family 1 task:

Provide a broken benchmark/harness scenario with these defects:
- timing records wall time but labels it as tokens/sec
- warm-up runs are included in scored CSVs
- blocked tasks are omitted from summary
- one malformed JSON input causes the parser to silently drop a row

Require:
- identify root causes
- propose minimum safe correction set
- provide patch/code or clear bounded implementation
- explain scoring exclusions
- avoid broad unrelated refactors

Evidence files:

[timing.py]
```python
import time


def record_run_metrics(prompt_tokens, completion_tokens, started_at):
    elapsed = time.time() - started_at
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "tokens_per_second": elapsed,
    }
```

[aggregate_scores.py]
```python
import csv
from pathlib import Path


def load_rows(scores_dir: Path):
    rows = []
    for path in scores_dir.glob("*.csv"):
        with path.open() as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                rows.append(row)
    return rows


def scored_rows(rows):
    return [row for row in rows]
```

[summary.py]
```python
def summarize_task_status(task_results):
    lines = []
    for task_name, status in sorted(task_results.items()):
        if status == "blocked":
            continue
        lines.append(f"{task_name}: {status}")
    return "\n".join(lines)
```

[parse_logs.py]
```python
import json


def parse_log_line(line):
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None
```

Explain which rows should be excluded from scoring and why.
