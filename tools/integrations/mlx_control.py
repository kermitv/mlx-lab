"""CLI-side read-only adapter for consuming ``mlx_control``."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from mlx_control import (
    ControlState,
    HealthStatus,
    HealthSummary,
    MLXController,
    ModelRegistrySnapshot,
    ModelRegistryState,
)


@dataclass(frozen=True)
class CLIStatusModelView:
    """Operator-facing model inventory entry for CLI rendering."""

    model_id: str
    ready: bool
    display_name: Optional[str] = None
    revision: Optional[str] = None


@dataclass(frozen=True)
class CLIStatusView:
    """Small operator-facing status snapshot built from ``MLXController``."""

    active_model_id: Optional[str]
    active_model_display_name: Optional[str]
    active_model_revision: Optional[str]
    health_status: HealthStatus
    health_summary: str
    registered_models: Tuple[CLIStatusModelView, ...]
    ready_models: Tuple[CLIStatusModelView, ...]


def load_controller_from_repo_local_context(
    *,
    connectivity_path: Optional[Path] = None,
    search_root: Optional[Path] = None,
) -> MLXController:
    """Load a prepared controller from repo-local benchmark visibility artifacts."""

    resolved_path = connectivity_path or _discover_latest_connectivity_artifact(
        search_root or _repo_root()
    )
    if resolved_path is None:
        return MLXController(state=ControlState())
    return load_controller_from_connectivity_artifact(resolved_path)


def load_controller_from_connectivity_artifact(path: Path) -> MLXController:
    """Build a read-only controller from a saved local-connectivity artifact."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    registry = ModelRegistryState(
        models=tuple(
            ModelRegistrySnapshot(
                model_id=item["id"],
                display_name=item.get("id"),
                ready=True,
            )
            for item in payload.get("data", [])
            if item.get("id")
        )
    )
    return MLXController(
        state=ControlState.stopped(
            health=HealthSummary(
                status=HealthStatus.HEALTHY,
                summary="loaded from %s" % _display_path(path),
            ),
            registry=registry,
        )
    )


def build_status_view(controller: MLXController) -> CLIStatusView:
    """Build a CLI status view from controller reads only."""

    active_model = controller.active_model()
    health = controller.health()
    registered_models = tuple(
        CLIStatusModelView(
            model_id=model.model_id,
            display_name=model.display_name,
            revision=model.revision,
            ready=model.ready,
        )
        for model in controller.list_models()
    )
    ready_models = tuple(model for model in registered_models if model.ready)
    return CLIStatusView(
        active_model_id=active_model.model_id if active_model else None,
        active_model_display_name=active_model.display_name if active_model else None,
        active_model_revision=active_model.revision if active_model else None,
        health_status=health.status,
        health_summary=health.summary,
        registered_models=registered_models,
        ready_models=ready_models,
    )


def render_status_view(view: CLIStatusView) -> str:
    """Render a compact human-readable status view."""

    lines = [
        "MLX Control Status",
        "Active model: %s" % _format_active_model(view),
        "Health: %s (%s)" % (view.health_status.value, view.health_summary),
        "Registered models: %s" % _format_model_list(view.registered_models),
        "Ready models: %s" % _format_model_list(view.ready_models),
    ]
    return "\n".join(lines) + "\n"


def _discover_latest_connectivity_artifact(search_root: Path) -> Optional[Path]:
    """Return the most recent benchmark local-connectivity artifact when present."""

    candidates = sorted(search_root.glob("benchmark-runs/*/logs/local-connectivity.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _repo_root() -> Path:
    """Return the repository root for repo-local CLI discovery."""

    return Path(__file__).resolve().parents[2]


def _display_path(path: Path) -> str:
    """Render a human-readable path relative to the repo when possible."""

    try:
        return str(path.relative_to(_repo_root()))
    except ValueError:
        return str(path)


def _format_active_model(view: CLIStatusView) -> str:
    """Format the active model line for operator-facing output."""

    if view.active_model_id is None:
        return "none"

    label = view.active_model_display_name or view.active_model_id
    if label == view.active_model_id:
        if view.active_model_revision:
            return "%s @ %s" % (view.active_model_id, view.active_model_revision)
        return view.active_model_id

    suffix = " [%s]" % view.active_model_id
    if view.active_model_revision:
        suffix += " @ %s" % view.active_model_revision
    return label + suffix


def _format_model_list(models: Tuple[CLIStatusModelView, ...]) -> str:
    """Format a model list in one compact line."""

    if not models:
        return "none"
    return ", ".join(_format_model(model) for model in models)


def _format_model(model: CLIStatusModelView) -> str:
    """Format one model inventory entry for status output."""

    label = model.display_name or model.model_id
    if label == model.model_id:
        rendered = model.model_id
    else:
        rendered = "%s [%s]" % (label, model.model_id)
    if model.revision:
        rendered += " @ %s" % model.revision
    if model.ready:
        rendered += " (ready)"
    return rendered
