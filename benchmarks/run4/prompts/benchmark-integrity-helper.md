Benchmark family 2 task:

Create or repair a helper script that:
- validates benchmark artifact completeness
- verifies both score CSVs exist
- checks blocked tasks are represented in summary
- stays bounded to the benchmark workspace
- emits clear exit codes and operator-readable results

Require:
- bounded implementation
- no mutation outside benchmark workspace
- clear maintainability
- practical operator value

Existing broken helper:
```python
#!/usr/bin/env python3
from pathlib import Path
import sys


def main(argv):
    run_dir = Path(argv[1]).resolve()
    required = [
        run_dir / "summary.md",
        run_dir / "scores" / "quality_scores.csv",
        run_dir / "scores" / "operational_scores.csv",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("missing required files")
        return 0
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

Provide either a repaired script or a bounded replacement. Include the code directly.
