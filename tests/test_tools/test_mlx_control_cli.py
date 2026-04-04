"""Tests for the Phase 3A repo-local ``mlx_control`` CLI slice."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from mlx_control import (
    ControlState,
    HealthStatus,
    HealthSummary,
    MLXController,
    ModelRegistrySnapshot,
    ModelRegistryState,
)
from tools.integrations.mlx_control import (
    CLIStatusModelView,
    build_status_view,
    load_controller_from_connectivity_artifact,
    load_controller_from_repo_local_context,
    render_status_view,
)
from tools.mlx_control_cli import main


def test_build_status_view_consumes_controller_reads() -> None:
    """The CLI adapter should build one operator-facing snapshot."""

    controller = MLXController(
        state=ControlState.running(
            "model-a",
            display_name="Model A",
            revision="main",
            health=HealthSummary(
                status=HealthStatus.DEGRADED,
                summary="read-only placeholder",
            ),
            registry=ModelRegistryState(
                models=(
                    ModelRegistrySnapshot(
                        model_id="model-a",
                        display_name="Model A",
                        revision="main",
                        ready=True,
                    ),
                    ModelRegistrySnapshot(
                        model_id="model-b",
                        display_name="Model B",
                        revision="staged",
                        ready=False,
                    ),
                ),
            ),
        )
    )

    view = build_status_view(controller)

    assert view.active_model_id == "model-a"
    assert view.active_model_display_name == "Model A"
    assert view.active_model_revision == "main"
    assert view.health_status is HealthStatus.DEGRADED
    assert view.health_summary == "read-only placeholder"
    assert view.registered_models == (
        CLIStatusModelView(
            model_id="model-a",
            display_name="Model A",
            revision="main",
            ready=True,
        ),
        CLIStatusModelView(
            model_id="model-b",
            display_name="Model B",
            revision="staged",
            ready=False,
        ),
    )
    assert view.ready_models == (
        CLIStatusModelView(
            model_id="model-a",
            display_name="Model A",
            revision="main",
            ready=True,
        ),
    )


def test_render_status_view_formats_compact_human_output() -> None:
    """Rendered output should stay compact and operator-readable."""

    view = build_status_view(
        MLXController(
            state=ControlState.running(
                "model-a",
                display_name="Model A",
                revision="main",
                health=HealthSummary(
                    status=HealthStatus.HEALTHY,
                    summary="status available",
                ),
                registry=ModelRegistryState(
                    models=(
                        ModelRegistrySnapshot(
                            model_id="model-a",
                            display_name="Model A",
                            revision="main",
                            ready=True,
                        ),
                        ModelRegistrySnapshot(
                            model_id="model-b",
                            ready=False,
                        ),
                    ),
                ),
            )
        )
    )

    rendered = render_status_view(view)

    assert "MLX Control Status" in rendered
    assert "Active model: Model A [model-a] @ main" in rendered
    assert "Health: healthy (status available)" in rendered
    assert "Registered models: Model A [model-a] @ main (ready), model-b" in rendered
    assert "Ready models: Model A [model-a] @ main (ready)" in rendered


def test_cli_status_command_renders_default_inert_snapshot() -> None:
    """The CLI should support the approved status command with no runtime access."""

    stdout = StringIO()
    with redirect_stdout(stdout):
        exit_code = main(["status"])

    rendered = stdout.getvalue()

    assert exit_code == 0
    assert "MLX Control Status" in rendered
    assert "Active model: none" in rendered
    assert "Health: unknown (health unknown)" in rendered
    assert "Registered models: none" in rendered
    assert "Ready models: none" in rendered


def test_cli_status_command_accepts_injected_controller() -> None:
    """The entrypoint should accept a prepared controller for controlled callers."""

    stdout = StringIO()
    controller = MLXController(
        state=ControlState.stopped(
            health=HealthSummary(
                status=HealthStatus.UNKNOWN,
                summary="runtime not implemented",
            ),
            registry=ModelRegistryState(
                models=(ModelRegistrySnapshot(model_id="model-a", ready=True),),
            ),
        )
    )

    with redirect_stdout(stdout):
        exit_code = main(["status"], controller=controller)

    rendered = stdout.getvalue()

    assert exit_code == 0
    assert "Health: unknown (runtime not implemented)" in rendered
    assert "Registered models: model-a (ready)" in rendered
    assert "Ready models: model-a (ready)" in rendered


def test_load_controller_from_connectivity_artifact_builds_real_snapshot() -> None:
    """Repo-local connectivity artifacts should build a real read-only controller."""

    with TemporaryDirectory() as tmpdir:
        artifact_path = Path(tmpdir) / "local-connectivity.json"
        artifact_path.write_text(
            json.dumps(
                {
                    "object": "list",
                    "data": [
                        {"id": "model-a", "object": "model"},
                        {"id": "model-b", "object": "model"},
                    ],
                }
            ),
            encoding="utf-8",
        )

        controller = load_controller_from_connectivity_artifact(artifact_path)
        view = build_status_view(controller)

    assert view.active_model_id is None
    assert view.health_status is HealthStatus.HEALTHY
    assert "loaded from " in view.health_summary
    assert tuple(model.model_id for model in view.registered_models) == (
        "model-a",
        "model-b",
    )
    assert tuple(model.model_id for model in view.ready_models) == (
        "model-a",
        "model-b",
    )


def test_load_controller_from_repo_local_context_discovers_latest_artifact() -> None:
    """Repo-local context loading should prefer the latest connectivity artifact."""

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        older = root / "benchmark-runs" / "run-old" / "logs" / "local-connectivity.json"
        newer = root / "benchmark-runs" / "run-new" / "logs" / "local-connectivity.json"
        older.parent.mkdir(parents=True, exist_ok=True)
        newer.parent.mkdir(parents=True, exist_ok=True)
        older.write_text(
            json.dumps({"object": "list", "data": [{"id": "model-old"}]}),
            encoding="utf-8",
        )
        newer.write_text(
            json.dumps({"object": "list", "data": [{"id": "model-new"}]}),
            encoding="utf-8",
        )
        newer.touch()

        controller = load_controller_from_repo_local_context(search_root=root)
        view = build_status_view(controller)

    assert tuple(model.model_id for model in view.registered_models) == ("model-new",)


def test_cli_status_command_supports_repo_local_connectivity_path() -> None:
    """The CLI should accept an explicit repo-local connectivity artifact path."""

    with TemporaryDirectory() as tmpdir:
        artifact_path = Path(tmpdir) / "local-connectivity.json"
        artifact_path.write_text(
            json.dumps(
                {
                    "object": "list",
                    "data": [
                        {"id": "model-a"},
                        {"id": "model-b"},
                    ],
                }
            ),
            encoding="utf-8",
        )

        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(
                ["status", "--connectivity-path", str(artifact_path)]
            )

    rendered = stdout.getvalue()

    assert exit_code == 0
    assert "Health: healthy (loaded from " in rendered
    assert "Registered models: model-a (ready), model-b (ready)" in rendered
    assert "Ready models: model-a (ready), model-b (ready)" in rendered
