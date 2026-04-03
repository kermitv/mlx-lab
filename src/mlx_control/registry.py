"""Model inventory contracts for the internal ``mlx_control`` module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass(frozen=True)
class ModelRegistrySnapshot:
    """Typed model inventory entry visible to the controller surface."""

    model_id: str
    display_name: Optional[str] = None
    revision: Optional[str] = None
    ready: bool = False


@dataclass(frozen=True)
class ModelRegistryState:
    """Read-only registry state owned by the canonical control state."""

    models: Tuple[ModelRegistrySnapshot, ...] = field(default_factory=tuple)

    @property
    def model_ids(self) -> Tuple[str, ...]:
        """Return the registry model identifiers in snapshot order."""

        return tuple(model.model_id for model in self.models)

    def get(self, model_id: str) -> Optional[ModelRegistrySnapshot]:
        """Return a registry entry when it is present in the snapshot."""

        for model in self.models:
            if model.model_id == model_id:
                return model
        return None

    def contains(self, model_id: str) -> bool:
        """Return whether a model identifier is present in the snapshot."""

        return self.get(model_id) is not None

    def ready_models(self) -> Tuple[ModelRegistrySnapshot, ...]:
        """Return only models marked ready in the snapshot."""

        return tuple(model for model in self.models if model.ready)
