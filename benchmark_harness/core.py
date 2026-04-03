#!/usr/bin/env python3
import csv
import importlib
import json
import os
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


@dataclass(frozen=True)
class TaskSpec:
    slug: str
    kind: str
    title: str


@dataclass(frozen=True)
class ModelSpec:
    id: str
    lane: str
    adapter: str
    required: bool = False
    display_name: Optional[str] = None
    smoke_prompt: str = "Reply with OK only."
    retry_empty_length: bool = False
    max_tokens: int = 900
    retry_max_tokens: int = 1800


@dataclass(frozen=True)
class BenchmarkConfig:
    run_name: str
    purpose: str
    execution_mode: str
    run_dir: Path
    local_endpoint: str
    tasks: list[TaskSpec]
    models: list[ModelSpec]


@dataclass(frozen=True)
class RunPaths:
    run_dir: Path
    coding_dir: Path
    reasoning_dir: Path
    solutions_dir: Path
    raw_local_dir: Path
    raw_frontier_dir: Path
    supervisor_dir: Path
    scores_dir: Path
    logs_dir: Path
    status_path: Path
    summary_path: Path
    run_log: Path
    local_connectivity_path: Path
    quality_csv: Path
    operational_csv: Path
    resource_csv: Path


def load_config(path: Path) -> BenchmarkConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    tasks = [TaskSpec(**item) for item in data["tasks"]]
    models = [ModelSpec(**item) for item in data["models"]]
    return BenchmarkConfig(
        run_name=data["run_name"],
        purpose=data["purpose"],
        execution_mode=data["execution_mode"],
        run_dir=Path(data["run_dir"]),
        local_endpoint=data["local_endpoint"],
        tasks=tasks,
        models=models,
    )


def build_paths(run_dir: Path) -> RunPaths:
    return RunPaths(
        run_dir=run_dir,
        coding_dir=run_dir / "coding",
        reasoning_dir=run_dir / "reasoning",
        solutions_dir=run_dir / "solutions",
        raw_local_dir=run_dir / "raw" / "local",
        raw_frontier_dir=run_dir / "raw" / "frontier",
        supervisor_dir=run_dir / "supervisor",
        scores_dir=run_dir / "scores",
        logs_dir=run_dir / "logs",
        status_path=run_dir / "supervisor" / "status.md",
        summary_path=run_dir / "summary.md",
        run_log=run_dir / "logs" / "run.log",
        local_connectivity_path=run_dir / "logs" / "local-connectivity.json",
        quality_csv=run_dir / "scores" / "quality_scores.csv",
        operational_csv=run_dir / "scores" / "operational_scores.csv",
        resource_csv=run_dir / "scores" / "resource_metrics.csv",
    )


class BenchmarkRunner:
    def __init__(self, config: BenchmarkConfig, callbacks: Any):
        self.config = config
        self.callbacks = callbacks
        self.paths = build_paths(config.run_dir)

    def now_iso(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())

    def safe_model(self, model: str) -> str:
        return model.replace("/", "_")

    def append_log(self, message: str) -> None:
        self.paths.run_log.parent.mkdir(parents=True, exist_ok=True)
        with self.paths.run_log.open("a", encoding="utf-8") as fh:
            fh.write("[%s] %s\n" % (self.now_iso(), message))

    def save_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def save_json(self, path: Path, obj: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    def http_json(self, url: str, payload: Any = None, timeout: int = 300, headers: Optional[dict[str, str]] = None) -> Any:
        req_headers = dict(headers or {})
        data = None
        method = "GET"
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
            method = "POST"
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)

    def run_cmd(self, command: str) -> tuple[bool, str]:
        try:
            out = subprocess.check_output(["/bin/zsh", "-lc", command], text=True, stderr=subprocess.STDOUT)
            return True, out
        except Exception as exc:  # noqa: BLE001
            return False, str(exc)

    def get_server_pid(self) -> tuple[Optional[str], str]:
        ok, out = self.run_cmd("lsof -nP -iTCP:8080 -sTCP:LISTEN")
        if not ok:
            return None, out.strip()
        lines = [line for line in out.splitlines() if line.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                return parts[1], out.strip()
        return None, out.strip()

    def capture_vm_stat(self) -> dict[str, Any]:
        ok, out = self.run_cmd("vm_stat | sed -n '1,20p'")
        return {"ok": ok, "text": out.strip()}

    def capture_top(self, pid: Optional[str]) -> dict[str, Any]:
        if not pid:
            return {"ok": False, "text": "top blocked: no server pid"}
        ok, out = self.run_cmd("top -l 1 -pid %s -stats pid,command,cpu,mem,vsize,rsize,state,time -n 5 | sed -n '1,20p'" % pid)
        return {"ok": ok, "text": out.strip()}

    def capture_process_stats(self, pid: Optional[str]) -> dict[str, Any]:
        if not pid:
            return {
                "ok": False,
                "cpu_percent_snapshot": None,
                "mem_percent_snapshot": None,
                "rss_snapshot": None,
                "vsz_snapshot": None,
                "text": "ps blocked: no server pid",
            }
        ok, out = self.run_cmd("ps -p %s -o %%cpu=,%%mem=,rss=,vsz=" % pid)
        if not ok:
            return {
                "ok": False,
                "cpu_percent_snapshot": None,
                "mem_percent_snapshot": None,
                "rss_snapshot": None,
                "vsz_snapshot": None,
                "text": out.strip(),
            }
        fields = out.strip().split()
        values = fields + [None] * (4 - len(fields))
        return {
            "ok": True,
            "cpu_percent_snapshot": values[0],
            "mem_percent_snapshot": values[1],
            "rss_snapshot": values[2],
            "vsz_snapshot": values[3],
            "text": out.strip(),
        }

    def snapshot_local_telemetry(self, model: str, task: str, phase: str) -> dict[str, Any]:
        pid, pid_note = self.get_server_pid()
        vm_stat = self.capture_vm_stat()
        top = self.capture_top(pid)
        proc = self.capture_process_stats(pid)
        path = self.paths.logs_dir / ("telemetry-%s-%s-%s.txt" % (self.safe_model(model), task, phase))
        content = [
            "timestamp_%s: %s" % (phase, self.now_iso()),
            "model: %s" % model,
            "task: %s" % task,
            "server_pid: %s" % pid,
            "pid_source: %s" % pid_note,
            "cpu_percent_snapshot: %s" % proc["cpu_percent_snapshot"],
            "mem_percent_snapshot: %s" % proc["mem_percent_snapshot"],
            "rss_snapshot: %s" % proc["rss_snapshot"],
            "vsz_snapshot: %s" % proc["vsz_snapshot"],
            "",
            "## vm_stat",
            vm_stat["text"],
            "",
            "## top",
            top["text"],
            "",
            "## process",
            proc["text"],
        ]
        self.save_text(path, "\n".join(content) + "\n")
        return {
            "server_pid": pid,
            "cpu_percent_snapshot": proc["cpu_percent_snapshot"],
            "mem_percent_snapshot": proc["mem_percent_snapshot"],
            "rss_snapshot": proc["rss_snapshot"],
            "vsz_snapshot": proc["vsz_snapshot"],
            "telemetry_ok": bool(vm_stat["ok"] and top["ok"] and proc["ok"]),
            "note": "vm_stat_ok=%s top_ok=%s process_ok=%s" % (vm_stat["ok"], top["ok"], proc["ok"]),
            "path": str(path),
        }

    def extract_chat_text(self, obj: dict[str, Any]) -> dict[str, Any]:
        choice = obj["choices"][0]
        message = choice.get("message", {})
        text = message.get("content", "") or ""
        usage = obj.get("usage", {})
        reasoning_value = message.get("reasoning")
        return {
            "text": text,
            "finish_reason": choice.get("finish_reason"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "content_empty": not bool(text.strip()),
            "reasoning_field_present": reasoning_value is not None and reasoning_value != "",
        }

    def extract_responses_text(self, obj: dict[str, Any]) -> dict[str, Any]:
        text_parts = []
        reasoning_present = False
        for item in obj.get("output", []):
            if item.get("type") == "reasoning":
                reasoning_present = True
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        text_parts.append(content.get("text", ""))
        usage = obj.get("usage", {})
        text = "\n".join([part for part in text_parts if part]).strip()
        return {
            "text": text,
            "finish_reason": obj.get("status"),
            "prompt_tokens": usage.get("input_tokens"),
            "completion_tokens": usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "content_empty": not bool(text.strip()),
            "reasoning_field_present": reasoning_present,
        }

    def openai_headers(self) -> dict[str, str]:
        return {"Authorization": "Bearer %s" % os.environ["OPENAI_API_KEY"]}

    def local_chat(self, model: ModelSpec, messages: list[dict[str, str]], max_tokens: Optional[int] = None) -> tuple[Any, Any, dict[str, Any]]:
        payload = {
            "model": model.id,
            "messages": messages,
            "temperature": 0,
            "max_tokens": max_tokens or model.max_tokens,
        }
        response = self.http_json(self.config.local_endpoint + "/chat/completions", payload=payload, timeout=900)
        return payload, response, self.extract_chat_text(response)

    def openai_chat(self, model: ModelSpec, messages: list[dict[str, str]], max_tokens: Optional[int] = None) -> tuple[Any, Any, dict[str, Any]]:
        payload = {
            "model": model.id,
            "messages": messages,
            "max_completion_tokens": max_tokens or model.max_tokens,
        }
        response = self.http_json(OPENAI_CHAT_URL, payload=payload, timeout=900, headers=self.openai_headers())
        return payload, response, self.extract_chat_text(response)

    def openai_responses(self, model: ModelSpec, prompt_text: str, max_tokens: Optional[int] = None) -> tuple[Any, Any, dict[str, Any]]:
        payload = {
            "model": model.id,
            "input": prompt_text,
            "max_output_tokens": max_tokens or model.max_tokens,
        }
        response = self.http_json(OPENAI_RESPONSES_URL, payload=payload, timeout=900, headers=self.openai_headers())
        return payload, response, self.extract_responses_text(response)

    def smoke_model(self, model: ModelSpec) -> tuple[bool, str, Any, Any]:
        try:
            if model.adapter in {"local_chat", "openai_chat"}:
                fn = self.local_chat if model.adapter == "local_chat" else self.openai_chat
                payload, response, parsed = fn(model, [{"role": "user", "content": model.smoke_prompt}], max_tokens=16)
            else:
                payload, response, parsed = self.openai_responses(model, model.smoke_prompt, max_tokens=16)
            return True, "finish_reason=%s" % parsed["finish_reason"], payload, response
        except Exception as exc:  # noqa: BLE001
            return False, str(exc), None, None

    def frontier_retry_messages(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        retry_note = (
            "Retry note:\n"
            "The previous attempt exhausted output budget without returning visible answer text.\n"
            "Keep hidden reasoning minimal and prioritize a concise visible answer with the requested sections."
        )
        return messages + [{"role": "user", "content": retry_note}]

    def update_status(self, state: dict[str, list[str]]) -> None:
        lines = [
            "# Benchmark Supervisor Status",
            "",
            "Updated: %s" % self.now_iso(),
            "",
            "## Overview",
        ]
        lines.extend(state["overview"])
        sections = ["connectivity", "warmup"] + [task.slug for task in self.config.tasks] + ["scores", "artifacts", "verdict"]
        for section in sections:
            lines.append("")
            lines.append("## %s" % section.replace("-", " ").title())
            lines.extend(state[section])
        self.save_text(self.paths.status_path, "\n".join(lines) + "\n")

    def model_request_for_task(self, task: TaskSpec, current_results_summary: str) -> tuple[str, list[dict[str, str]], str]:
        problem = self.callbacks.build_problem_text(task.slug, current_results_summary)
        header = self.callbacks.prompt_header(task)
        combined = header + "\n\n" + problem
        messages = [{"role": "user", "content": combined}]
        return problem, messages, combined

    def retry_once(self, fn: Any) -> tuple[Any, int, Optional[str]]:
        try:
            return fn(), 0, None
        except Exception as exc1:  # noqa: BLE001
            try:
                time.sleep(1)
                return fn(), 1, str(exc1)
            except Exception as exc2:  # noqa: BLE001
                raise RuntimeError("first attempt failed: %s; retry failed: %s" % (exc1, exc2))

    def operational_score(self, meta: dict[str, Any], blocked: bool, retries_used: int) -> float:
        if blocked:
            return 0.0
        score = 10.0
        if retries_used:
            score -= 1.0
        if meta["content_empty"]:
            score -= 3.0
        elapsed = meta["elapsed_seconds"]
        if elapsed > 180:
            score -= 3.5
        elif elapsed > 90:
            score -= 2.5
        elif elapsed > 45:
            score -= 1.5
        elif elapsed > 20:
            score -= 0.75
        finish_reason = str(meta["finish_reason"]).lower() if meta["finish_reason"] is not None else ""
        if finish_reason not in {"stop", "completed"}:
            score -= 1.0
        return round(max(score, 0.0), 2)

    def summarize_current_results(self, results: dict[str, dict[str, Any]]) -> str:
        lines = []
        for model, model_results in sorted(results.items()):
            if not model_results:
                continue
            lines.append("Model: %s" % model)
            for task_slug, data in sorted(model_results.items()):
                lines.append(
                    "- %s: quality=%.2f operational=%.2f blocked=%s retries=%s note=%s"
                    % (
                        task_slug,
                        data["quality_score"],
                        data["operational_score"],
                        data["blocked"],
                        data["retries_used"],
                        data["verdict_note"],
                    )
                )
            lines.append("")
        return "\n".join(lines).strip()

    def write_verdict(
        self,
        path: Path,
        task_slug: str,
        model: str,
        quality_score: float,
        operational_score_value: float,
        hits: list[str],
        meta: dict[str, Any],
        note: str,
    ) -> None:
        lines = [
            "# Verdict",
            "",
            "model: %s" % model,
            "task: %s" % task_slug,
            "quality_score_10: %.2f" % quality_score,
            "operational_score_10: %.2f" % operational_score_value,
            "elapsed_seconds: %.3f" % meta["elapsed_seconds"],
            "finish_reason: %s" % meta["finish_reason"],
            "retries_used: %s" % meta["retries_used"],
            "blocked: %s" % meta["blocked"],
            "telemetry_ok: %s" % meta["telemetry_ok"],
            "",
            "Evidence hits: %s" % (", ".join(hits) if hits else "none"),
            "Note: %s" % note,
        ]
        self.save_text(path, "\n".join(lines) + "\n")

    def write_quality_csv(self, models: list[ModelSpec], results: dict[str, dict[str, Any]]) -> None:
        task_headers = [task.slug.replace("-", "_") + "_quality_score_10" for task in self.config.tasks]
        headers = ["model"] + task_headers + ["overall_quality_score_10", "notes"]
        rows = []
        for model in models:
            model_results = results.get(model.id, {})
            task_scores = [model_results.get(task.slug, {}).get("quality_score", 0.0) for task in self.config.tasks]
            overall = round(sum(task_scores) / len(task_scores), 2)
            notes = "; ".join(
                "%s: %s" % (task.slug, model_results.get(task.slug, {}).get("verdict_note", "blocked"))
                for task in self.config.tasks
            )
            rows.append([model.id] + task_scores + [overall, notes])
        with self.paths.quality_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)
            writer.writerows(rows)

    def write_operational_csv(self, models: list[ModelSpec], results: dict[str, dict[str, Any]]) -> None:
        task_headers = [task.slug.replace("-", "_") + "_operational_score_10" for task in self.config.tasks]
        headers = ["model"] + task_headers + ["overall_operational_score_10", "retries_used", "human_rescue_required", "notes"]
        rows = []
        for model in models:
            model_results = results.get(model.id, {})
            task_scores = [model_results.get(task.slug, {}).get("operational_score", 0.0) for task in self.config.tasks]
            retries_used = sum(model_results.get(task.slug, {}).get("retries_used", 0) for task in self.config.tasks)
            overall = round(sum(task_scores) / len(task_scores), 2)
            notes = "; ".join(
                "%s: %s" % (task.slug, model_results.get(task.slug, {}).get("finish_reason", "blocked"))
                for task in self.config.tasks
            )
            rows.append([model.id] + task_scores + [overall, retries_used, "no", notes])
        with self.paths.operational_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)
            writer.writerows(rows)

    def write_resource_csv(self, resource_rows: list[list[Any]]) -> None:
        headers = [
            "model",
            "task",
            "elapsed_seconds",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "tokens_per_second",
            "finish_reason",
            "content_empty",
            "reasoning_field_present",
            "cpu_percent_snapshot",
            "mem_percent_snapshot",
            "rss_snapshot",
            "vsz_snapshot",
            "telemetry_ok",
            "notes",
        ]
        with self.paths.resource_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)
            for row in resource_rows:
                writer.writerow(row)

    def write_kind_summary(self, models: list[ModelSpec], results: dict[str, dict[str, Any]], kind: str, path: Path, title: str) -> None:
        lines = ["# %s" % title, ""]
        for task in [task for task in self.config.tasks if task.kind == kind]:
            lines.append("## %s" % task.slug)
            lines.append("")
            for model in models:
                data = results[model.id][task.slug]
                lines.append(
                    "- %s: quality %.2f, operational %.2f, blocked=%s, note=%s"
                    % (model.id, data["quality_score"], data["operational_score"], data["blocked"], data["verdict_note"])
                )
            lines.append("")
        self.save_text(path, "\n".join(lines).strip() + "\n")

    def verify_artifacts(self, expected_models: list[ModelSpec], state: dict[str, list[str]]) -> list[str]:
        missing = []
        for rel in [
            self.paths.coding_dir / "results.md",
            self.paths.reasoning_dir / "results.md",
            self.paths.quality_csv,
            self.paths.operational_csv,
            self.paths.resource_csv,
            self.paths.summary_path,
            self.paths.status_path,
            self.paths.local_connectivity_path,
        ]:
            if not rel.exists():
                missing.append(str(rel))
        for task in self.config.tasks:
            solution_dir = self.paths.solutions_dir / task.slug
            problem_path = solution_dir / "problem.md"
            if not problem_path.exists():
                missing.append(str(problem_path))
            for model in expected_models:
                request_path = solution_dir / ("request-%s.json" % self.safe_model(model.id))
                response_path = solution_dir / ("response-%s.json" % self.safe_model(model.id))
                answer_path = solution_dir / ("answer-%s.md" % self.safe_model(model.id))
                verdict_path = solution_dir / ("verdict-%s.md" % self.safe_model(model.id))
                for path in [request_path, response_path, answer_path, verdict_path]:
                    if not path.exists():
                        missing.append(str(path))
                raw_dir = self.paths.raw_local_dir if model.lane == "local" else self.paths.raw_frontier_dir
                raw_path = raw_dir / ("%s-%s.json" % (task.slug, self.safe_model(model.id)))
                if not raw_path.exists():
                    missing.append(str(raw_path))
        if missing:
            state["artifacts"] = ["missing artifacts:", *["- %s" % item for item in missing[:50]]]
        else:
            state["artifacts"] = ["all required summary, score, raw, request, response, answer, and verdict artifacts are present"]
        self.update_status(state)
        return missing

    def execute_model(self, model: ModelSpec, messages: list[dict[str, str]], combined_prompt: str) -> tuple[Any, Any, dict[str, Any], int, Optional[str]]:
        if model.adapter == "local_chat":
            fn = lambda: self.local_chat(model, messages, max_tokens=model.max_tokens)
        elif model.adapter == "openai_chat":
            fn = lambda: self.openai_chat(model, messages, max_tokens=model.max_tokens)
        elif model.adapter == "openai_responses":
            fn = lambda: self.openai_responses(model, combined_prompt, max_tokens=model.max_tokens)
        else:
            raise ValueError("unsupported adapter %s for %s" % (model.adapter, model.id))
        (payload, response, parsed), retries_used, retry_note = self.retry_once(fn)
        if model.retry_empty_length and parsed["content_empty"] and str(parsed["finish_reason"]).lower() == "length":
            retry_payload, retry_response, retry_parsed = self.openai_chat(
                model,
                self.frontier_retry_messages(messages),
                max_tokens=model.retry_max_tokens,
            )
            payload = {"initial_payload": payload, "retry_payload": retry_payload}
            response = {"initial_response": response, "retry_response": retry_response}
            parsed = retry_parsed
            retries_used = max(retries_used, 1)
            retry_note = "empty length-truncated output retried once with concise-answer instruction and larger completion budget"
        return payload, response, parsed, retries_used, retry_note

    def run(self) -> int:
        if not self.config.run_dir.exists():
            raise RuntimeError("run directory missing: %s" % self.config.run_dir)

        for path in [
            self.paths.coding_dir,
            self.paths.reasoning_dir,
            self.paths.solutions_dir,
            self.paths.raw_local_dir,
            self.paths.raw_frontier_dir,
            self.paths.supervisor_dir,
            self.paths.scores_dir,
            self.paths.logs_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

        self.append_log("%s starting" % self.config.run_name)
        state = {
            "overview": [
                "purpose: %s" % self.config.purpose,
                "execution mode: %s" % self.config.execution_mode,
                "run dir: %s" % self.config.run_dir,
            ],
            "connectivity": ["pending"],
            "warmup": ["pending"],
            "scores": ["pending"],
            "artifacts": ["pending"],
            "verdict": ["pending"],
        }
        for task in self.config.tasks:
            state[task.slug] = ["pending"]
        self.update_status(state)

        local_specs = [model for model in self.config.models if model.lane == "local"]
        frontier_specs = [model for model in self.config.models if model.lane == "frontier"]

        local_models_response = self.http_json(self.config.local_endpoint + "/models", timeout=60)
        self.save_json(self.paths.local_connectivity_path, local_models_response)
        visible_local_models = [item["id"] for item in local_models_response.get("data", [])]
        available_local_models = [model for model in local_specs if model.id in visible_local_models]
        missing_primary = [model.id for model in local_specs if model.required and model.id not in visible_local_models]
        state["connectivity"] = [
            "local endpoint ok: %s/models responded" % self.config.local_endpoint,
            "visible local models: %s" % ", ".join(visible_local_models),
            "available benchmarked local models: %s" % ", ".join(model.id for model in available_local_models),
        ]
        if missing_primary:
            state["connectivity"].append("missing required local models: %s" % ", ".join(missing_primary))

        frontier_available = []
        if frontier_specs:
            if "OPENAI_API_KEY" not in os.environ:
                state["connectivity"].append("frontier blocked: OPENAI_API_KEY missing")
            else:
                for model in frontier_specs:
                    ok, note, payload, response = self.smoke_model(model)
                    slug = self.safe_model(model.id)
                    if payload is not None:
                        self.save_json(self.paths.logs_dir / ("frontier-%s-smoke-request.json" % slug), payload)
                    if response is not None:
                        self.save_json(self.paths.logs_dir / ("frontier-%s-smoke-response.json" % slug), response)
                    if ok:
                        frontier_available.append(model)
                        state["connectivity"].append("%s smoke ok; %s" % (model.id, note))
                    else:
                        state["connectivity"].append("%s blocked; %s" % (model.id, note))
        self.update_status(state)

        if missing_primary:
            state["verdict"] = ["blocked: missing required local models"]
            self.update_status(state)
            return 1

        for model in available_local_models:
            self.append_log("Warm-up start for %s" % model.id)
            try:
                payload, response, _ = self.local_chat(model, [{"role": "user", "content": "Warm up only. Reply with warm."}], max_tokens=16)
                self.save_json(self.paths.logs_dir / ("warmup-request-%s.json" % self.safe_model(model.id)), payload)
                self.save_json(self.paths.logs_dir / ("warmup-response-%s.json" % self.safe_model(model.id)), response)
                self.append_log("Warm-up ok for %s" % model.id)
            except Exception as exc:  # noqa: BLE001
                self.append_log("Warm-up failed for %s: %s" % (model.id, exc))
            time.sleep(0.5)
        state["warmup"] = ["issued one excluded warm-up request per benchmarked local model"]
        self.update_status(state)

        benchmark_models = available_local_models + frontier_available
        results: dict[str, dict[str, Any]] = {model.id: {} for model in benchmark_models}
        resource_rows = []

        for task in self.config.tasks:
            current_results_summary = self.summarize_current_results(results)
            problem_text, messages, combined_prompt = self.model_request_for_task(task, current_results_summary or "No current results yet.")
            solution_dir = self.paths.solutions_dir / task.slug
            self.save_text(solution_dir / "problem.md", problem_text + "\n")
            state[task.slug] = ["running"]
            self.update_status(state)

            for model in benchmark_models:
                self.append_log("Task %s starting for %s" % (task.slug, model.id))
                request_path = solution_dir / ("request-%s.json" % self.safe_model(model.id))
                response_path = solution_dir / ("response-%s.json" % self.safe_model(model.id))
                answer_path = solution_dir / ("answer-%s.md" % self.safe_model(model.id))
                verdict_path = solution_dir / ("verdict-%s.md" % self.safe_model(model.id))
                raw_path = (self.paths.raw_local_dir if model.lane == "local" else self.paths.raw_frontier_dir) / ("%s-%s.json" % (task.slug, self.safe_model(model.id)))

                blocked = False
                retries_used = 0
                retry_note = ""
                pre = self.snapshot_local_telemetry(model.id, task.slug, "pre") if model.lane == "local" else {
                    "cpu_percent_snapshot": None,
                    "mem_percent_snapshot": None,
                    "rss_snapshot": None,
                    "vsz_snapshot": None,
                    "telemetry_ok": False,
                    "note": "local process telemetry not applicable",
                }
                started = time.time()
                payload = {}
                response = {}
                parsed = {
                    "text": "",
                    "finish_reason": "blocked",
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "total_tokens": None,
                    "content_empty": True,
                    "reasoning_field_present": False,
                }
                error_text = None
                try:
                    payload, response, parsed, retries_used, retry_note = self.execute_model(model, messages, combined_prompt)
                except Exception as exc:  # noqa: BLE001
                    blocked = True
                    error_text = str(exc)
                    response = {"error": error_text}
                    self.append_log("Task %s blocked for %s: %s" % (task.slug, model.id, exc))
                ended = time.time()
                post = self.snapshot_local_telemetry(model.id, task.slug, "post") if model.lane == "local" else {
                    "cpu_percent_snapshot": None,
                    "mem_percent_snapshot": None,
                    "rss_snapshot": None,
                    "vsz_snapshot": None,
                    "telemetry_ok": False,
                    "note": "local process telemetry not applicable",
                }
                elapsed = round(ended - started, 3)
                total_tokens = parsed["total_tokens"]
                tps = round(total_tokens / elapsed, 3) if total_tokens and elapsed > 0 else None
                answer_text = parsed["text"].strip()
                if blocked:
                    answer_text = "blocked\n\n%s" % error_text
                meta = {
                    "lane": model.lane,
                    "elapsed_seconds": elapsed,
                    "finish_reason": parsed["finish_reason"],
                    "prompt_tokens": parsed["prompt_tokens"],
                    "completion_tokens": parsed["completion_tokens"],
                    "total_tokens": total_tokens,
                    "tokens_per_second": tps,
                    "content_empty": parsed["content_empty"],
                    "reasoning_field_present": parsed["reasoning_field_present"],
                    "cpu_percent_snapshot": post["cpu_percent_snapshot"],
                    "mem_percent_snapshot": post["mem_percent_snapshot"],
                    "rss_snapshot": post["rss_snapshot"],
                    "vsz_snapshot": post["vsz_snapshot"],
                    "telemetry_ok": post["telemetry_ok"] if model.lane == "local" else False,
                    "blocked": blocked,
                    "retries_used": retries_used,
                }
                quality_score, hits = (0.0, []) if blocked else self.callbacks.score_quality(task.slug, answer_text)
                verdict_note = "blocked" if blocked else (", ".join(hits) if hits else "weak evidence coverage")
                op_score = self.operational_score(meta, blocked, retries_used)
                request_obj = {
                    "model": model.id,
                    "task": task.slug,
                    "lane": model.lane,
                    "adapter": model.adapter,
                    "messages": messages if model.adapter in {"local_chat", "openai_chat"} else None,
                    "prompt": combined_prompt if model.adapter == "openai_responses" else None,
                    "payload": payload,
                    "retries_used": retries_used,
                    "retry_note": retry_note,
                    "pre_telemetry": pre,
                }
                self.save_json(request_path, request_obj)
                self.save_json(response_path, response)
                self.save_json(raw_path, response)
                self.save_text(answer_path, answer_text + "\n")
                self.write_verdict(verdict_path, task.slug, model.id, quality_score, op_score, hits, meta, verdict_note)
                results[model.id][task.slug] = {
                    "quality_score": round(quality_score, 2),
                    "operational_score": op_score,
                    "blocked": blocked,
                    "retries_used": retries_used,
                    "finish_reason": parsed["finish_reason"],
                    "verdict_note": verdict_note,
                }
                resource_rows.append([
                    model.id,
                    task.slug,
                    elapsed,
                    parsed["prompt_tokens"],
                    parsed["completion_tokens"],
                    total_tokens,
                    tps,
                    parsed["finish_reason"],
                    parsed["content_empty"],
                    parsed["reasoning_field_present"],
                    post["cpu_percent_snapshot"],
                    post["mem_percent_snapshot"],
                    post["rss_snapshot"],
                    post["vsz_snapshot"],
                    meta["telemetry_ok"] if model.lane == "local" else "n/a",
                    post["note"],
                ])
                self.append_log(
                    "Task %s finished for %s: blocked=%s quality=%.2f operational=%.2f retries=%s elapsed=%.3f"
                    % (task.slug, model.id, blocked, quality_score, op_score, retries_used, elapsed)
                )

            state[task.slug] = [
                "%s: quality %.2f operational %.2f blocked=%s"
                % (
                    model.id,
                    results[model.id][task.slug]["quality_score"],
                    results[model.id][task.slug]["operational_score"],
                    results[model.id][task.slug]["blocked"],
                )
                for model in benchmark_models
            ]
            self.update_status(state)

        self.write_quality_csv(benchmark_models, results)
        self.write_operational_csv(benchmark_models, results)
        self.write_resource_csv(resource_rows)
        self.write_kind_summary(benchmark_models, results, "coding", self.paths.coding_dir / "results.md", "Coding Results")
        self.write_kind_summary(benchmark_models, results, "reasoning", self.paths.reasoning_dir / "results.md", "Reasoning Results")
        self.callbacks.write_summary(self, available_local_models, frontier_available, results)

        state["scores"] = [
            "quality_scores.csv written",
            "operational_scores.csv written",
            "resource_metrics.csv written",
        ]
        state["verdict"] = self.callbacks.final_verdict_lines(self, available_local_models, frontier_available, results)
        self.update_status(state)

        missing = self.verify_artifacts(benchmark_models, state)
        self.append_log("%s completed; missing_artifacts=%s" % (self.config.run_name, len(missing)))
        return 0 if not missing else 1


def load_callbacks(module_name: str) -> Any:
    return importlib.import_module(module_name)
