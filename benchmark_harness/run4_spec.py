#!/usr/bin/env python3
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
RUN3_DIR = ROOT / "benchmark-runs" / "run-20260329-run3"
RUN3_FIXTURES = RUN3_DIR / "fixtures"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def prompt_header(task) -> str:
    return dedent(
        """
        You are participating in a benchmark. Work only from the provided evidence.
        Be evidence-first, bounded, and explicit about uncertainty.
        Do not suggest broad unrelated refactors.
        Return concise markdown with these exact sections:
        ## Findings
        ## Minimum Safe Correction Set
        ## Evidence Boundaries
        ## Final Answer
        """
    ).strip()


def build_problem_text(task_slug: str, current_results_summary: str) -> str:
    if task_slug == "multi-file-repair":
        return dedent(
            """
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
            %s
            ```

            [aggregate_scores.py]
            ```python
            %s
            ```

            [summary.py]
            ```python
            %s
            ```

            [parse_logs.py]
            ```python
            %s
            ```

            Explain which rows should be excluded from scoring and why.
            """
        ).strip() % (
            read_text(RUN3_FIXTURES / "multi_file_repair" / "timing.py").strip(),
            read_text(RUN3_FIXTURES / "multi_file_repair" / "aggregate_scores.py").strip(),
            read_text(RUN3_FIXTURES / "multi_file_repair" / "summary.py").strip(),
            read_text(RUN3_FIXTURES / "multi_file_repair" / "parse_logs.py").strip(),
        )
    if task_slug == "benchmark-integrity-helper":
        return dedent(
            """
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
            %s
            ```

            Provide either a repaired script or a bounded replacement. Include the code directly.
            """
        ).strip() % read_text(RUN3_FIXTURES / "repo_engineering" / "validate_artifacts.py").strip()
    if task_slug == "partial-failure-debugging":
        return dedent(
            """
            Benchmark family 3 task:

            Provide:
            - inconsistent scores
            - malformed reasoning log
            - summary that overstates confidence
            - supervisor status claiming all tasks completed
            - partial evidence set with contradictions

            Require:
            - identify contradictions
            - infer likely root-cause sequence
            - propose minimum safe correction set
            - preserve evidence
            - distinguish correcting results from rewriting history

            Evidence:

            [notes.txt]
            ```
            %s
            ```

            [reasoning-log.json]
            ```json
            %s
            ```

            [scores.csv]
            ```csv
            %s
            ```

            [summary.md]
            ```markdown
            %s
            ```

            [supervisor-status.md]
            ```markdown
            %s
            ```
            """
        ).strip() % (
            read_text(RUN3_FIXTURES / "debugging_state" / "notes.txt").strip(),
            read_text(RUN3_FIXTURES / "debugging_state" / "reasoning-log.json").strip(),
            read_text(RUN3_FIXTURES / "debugging_state" / "scores.csv").strip(),
            read_text(RUN3_FIXTURES / "debugging_state" / "summary.md").strip(),
            read_text(RUN3_FIXTURES / "debugging_state" / "supervisor-status.md").strip(),
        )
    if task_slug == "escalation-boundary-decision":
        return dedent(
            """
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
            %s
            ```

            [run3 operational_scores.csv]
            ```csv
            %s
            ```

            Current run evidence so far:
            ```markdown
            %s
            ```
            """
        ).strip() % (
            read_text(RUN3_DIR / "scores" / "quality_scores.csv").strip(),
            read_text(RUN3_DIR / "scores" / "operational_scores.csv").strip(),
            current_results_summary.strip(),
        )
    raise ValueError("unknown task %s" % task_slug)


def contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def score_multi_file_repair(answer: str) -> tuple[float, list[str]]:
    text = answer.lower()
    points = 0.0
    hits = []
    if contains_any(text, ["tokens_per_second", "wall time", "elapsed"]):
        points += 2.0
        hits.append("timing metric defect")
    if contains_any(text, ["warm-up", "warmup"]) and contains_any(text, ["exclude", "scor", "csv"]):
        points += 2.0
        hits.append("warm-up scoring exclusion")
    if contains_any(text, ["blocked"]) and contains_any(text, ["summary", "omitted", "include"]):
        points += 2.0
        hits.append("blocked summary omission")
    if contains_any(text, ["malformed json", "jsondecodeerror", "silently drop", "return none"]):
        points += 2.0
        hits.append("malformed json row loss")
    if contains_any(text, ["minimum safe", "bounded", "avoid broad", "small patch", "surgical"]):
        points += 1.0
        hits.append("bounded correction set")
    if contains_any(text, ["scoring exclusion", "do not score", "exclude from scoring", "blocked rows should remain visible"]):
        points += 1.0
        hits.append("scoring exclusion rationale")
    return min(points, 10.0), hits


def score_integrity_helper(answer: str) -> tuple[float, list[str]]:
    text = answer.lower()
    points = 0.0
    hits = []
    if contains_any(text, ["quality_scores.csv", "operational_scores.csv"]):
        points += 2.0
        hits.append("both score csv checks")
    if contains_any(text, ["summary.md"]) and contains_any(text, ["blocked", "summary"]):
        points += 2.0
        hits.append("blocked tasks represented in summary")
    if contains_any(text, ["resolve()", "relative_to", "within the benchmark workspace", "workspace boundary", "run_dir.resolve"]):
        points += 2.0
        hits.append("workspace boundary guard")
    if contains_any(text, ["exit(", "return 1", "return 2", "exit code", "sys.exit"]):
        points += 2.0
        hits.append("clear exit codes")
    if contains_any(text, ["```python", "def main", "pathlib", "operator-readable", "missing required files"]):
        points += 2.0
        hits.append("bounded practical implementation")
    return min(points, 10.0), hits


def score_partial_failure(answer: str) -> tuple[float, list[str]]:
    text = answer.lower()
    points = 0.0
    hits = []
    if contains_any(text, ["contradiction", "blocked", "completed successfully", "all tasks completed"]):
        points += 2.0
        hits.append("contradictions identified")
    if contains_any(text, ["malformed reasoning log", "invalid json", "reasoning-log.json"]):
        points += 2.0
        hits.append("malformed log identified")
    if contains_any(text, ["root-cause sequence", "likely sequence", "pipeline", "ordering"]):
        points += 1.5
        hits.append("likely sequence inferred")
    if contains_any(text, ["preserve evidence", "do not rewrite history", "quarantine", "append correction"]):
        points += 2.0
        hits.append("evidence preservation")
    if contains_any(text, ["correcting results", "rewriting history", "amend summary", "status should be updated"]):
        points += 1.5
        hits.append("correction vs history distinction")
    if contains_any(text, ["minimum safe correction", "bounded"]):
        points += 1.0
        hits.append("bounded correction set")
    return min(points, 10.0), hits


def score_escalation(answer: str) -> tuple[float, list[str]]:
    text = answer.lower()
    points = 0.0
    hits = []
    if contains_any(text, ["task class", "routing", "use fast local default", "routine", "bounded"]):
        points += 2.0
        hits.append("task-class routing")
    if contains_any(text, ["coding specialist", "coder", "multi-file", "engineering repair"]):
        points += 2.0
        hits.append("coding specialist threshold")
    if contains_any(text, ["reasoning lane", "governance", "contradictions", "cross-artifact"]):
        points += 2.0
        hits.append("reasoning lane threshold")
    if contains_any(text, ["frontier", "high stakes", "promotion-grade", "materially better"]):
        points += 2.0
        hits.append("frontier escalation threshold")
    if contains_any(text, ["mlx-lab-only", "openclaw-runtime-lab", "missing evidence", "do not promote yet"]):
        points += 2.0
        hits.append("promotion boundary")
    return min(points, 10.0), hits


def score_quality(task_slug: str, answer: str) -> tuple[float, list[str]]:
    if task_slug == "multi-file-repair":
        return score_multi_file_repair(answer)
    if task_slug == "benchmark-integrity-helper":
        return score_integrity_helper(answer)
    if task_slug == "partial-failure-debugging":
        return score_partial_failure(answer)
    return score_escalation(answer)


def best_local_model(local_models, results, task_slugs):
    best = None
    best_score = -1.0
    for model in local_models:
        scores = [results[model.id][task]["quality_score"] for task in task_slugs]
        avg = sum(scores) / len(scores)
        if avg > best_score:
            best = model
            best_score = avg
    return best, round(best_score, 2)


def best_local_operational(local_models, results, tasks):
    best = None
    best_score = -1.0
    for model in local_models:
        scores = [results[model.id][task.slug]["operational_score"] for task in tasks]
        avg = sum(scores) / len(scores)
        if avg > best_score:
            best = model
            best_score = avg
    return best, round(best_score, 2)


def frontier_materially_better(frontier_models, local_models, results, tasks):
    if not frontier_models:
        best_local = max(local_models, key=lambda model: sum(results[model.id][task.slug]["quality_score"] for task in tasks) / len(tasks))
        local_avg = sum(results[best_local.id][task.slug]["quality_score"] for task in tasks) / len(tasks)
        return False, None, 0.0, best_local, round(local_avg, 2)
    best_frontier = max(frontier_models, key=lambda model: sum(results[model.id][task.slug]["quality_score"] for task in tasks) / len(tasks))
    best_local = max(local_models, key=lambda model: sum(results[model.id][task.slug]["quality_score"] for task in tasks) / len(tasks))
    frontier_avg = sum(results[best_frontier.id][task.slug]["quality_score"] for task in tasks) / len(tasks)
    local_avg = sum(results[best_local.id][task.slug]["quality_score"] for task in tasks) / len(tasks)
    return frontier_avg >= local_avg + 1.0, best_frontier, round(frontier_avg, 2), best_local, round(local_avg, 2)


def write_summary(runner, local_models, frontier_models, results):
    best_default, best_default_score = best_local_operational(local_models, results, runner.config.tasks)
    best_coding, best_coding_score = best_local_model(local_models, results, ["multi-file-repair", "benchmark-integrity-helper"])
    best_reasoning, best_reasoning_score = best_local_model(local_models, results, ["partial-failure-debugging", "escalation-boundary-decision"])
    materially_better, best_frontier, best_frontier_score, best_local, best_local_score = frontier_materially_better(
        frontier_models,
        local_models,
        results,
        runner.config.tasks,
    )
    lines = [
        "# %s Summary" % runner.config.run_name,
        "",
        "1. Run completion time",
        runner.now_iso(),
        "",
        "2. Local models benchmarked",
        ", ".join(model.id for model in local_models),
        "",
        "3. Frontier models benchmarked",
        ", ".join(model.id for model in frontier_models) if frontier_models else "none available",
        "",
        "4. Best local operational default",
        "%s (overall operational %.2f)" % (best_default.id, best_default_score),
        "",
        "5. Best local coding-capable model",
        "%s (coding quality %.2f)" % (best_coding.id, best_coding_score),
        "",
        "6. Best local reasoning/governance model",
        "%s (reasoning quality %.2f)" % (best_reasoning.id, best_reasoning_score),
        "",
        "7. Whether frontier materially outperformed the best local model",
        "yes: %s %.2f vs %s %.2f (>= 1.0 quality-point gap)"
        % (best_frontier.id, best_frontier_score, best_local.id, best_local_score)
        if materially_better
        else "no: %s %.2f vs %s %.2f (< 1.0 quality-point gap)"
        % ((best_frontier.id if best_frontier else "none"), best_frontier_score, best_local.id, best_local_score),
        "",
        "8. Recommended routing thresholds by task type",
        "- Fast local default: routine bounded drafting, shallow repo hygiene, low-risk artifact checks, and narrow single-hop questions.",
        "- Stronger local coding specialist: multi-file repair, patch planning, and code-generation tasks that need concrete file-level changes but remain bounded to local evidence.",
        "- Stronger local reasoning lane: contradiction analysis, partial-failure reconstruction, governance-sensitive summaries, and cross-artifact reconciliation inside mlx-lab.",
        "- Escalate to frontier: ambiguous high-stakes routing, promotion-grade governance decisions, unclear evidence with conflicting states, or when the local answer misses required boundaries on the first pass.",
        "",
        "9. Which conclusions are safe for mlx-lab only",
        "- Model-specific routing inside this local MLX-served environment.",
        "- Observed local latency, formatting reliability, and evidence-handling behavior for this host and current endpoint shape.",
        "- Relative usefulness of the tested local models for these benchmark families.",
        "",
        "10. What evidence is still missing for promotion into openclaw-runtime-lab",
        "- Repeated runs across more repos and failure modes.",
        "- Promotion-grade evidence for production topology, cost envelopes, and unattended recovery under real operator workflows.",
        "- Independent verification that routing recommendations remain stable beyond this mlx-lab host and model set.",
        "",
        "11. What should be benchmarked next",
        "- Longer-context repo repair with concrete patch application and validation.",
        "- Mixed coding plus governance tasks with stricter answer-shape enforcement.",
        "- Repeated frontier-vs-local runs to test variance and retry sensitivity.",
    ]
    runner.save_text(runner.paths.summary_path, "\n".join(lines) + "\n")


def final_verdict_lines(runner, local_models, frontier_models, results):
    materially_better, best_frontier, best_local_score_frontier, best_local, best_local_score = frontier_materially_better(
        frontier_models,
        local_models,
        results,
        runner.config.tasks,
    )
    return [
        "short routing verdict:",
        "- fast local default stays with the strongest operational local model for bounded tasks",
        "- escalate to stronger local specialist for multi-file coding or cross-artifact reasoning before frontier",
        "- frontier %s materially outperform the best local model (%s %.2f vs %s %.2f)"
        % ("did" if materially_better else "did not", (best_frontier.id if best_frontier else "none"), best_local_score_frontier, best_local.id, best_local_score),
        "- conclusions remain mlx-lab-only until repeated promotion-grade evidence exists",
    ]
