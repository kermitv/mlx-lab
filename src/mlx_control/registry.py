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

    def get(self, model_id: str) -> Optional[ModelRegistrySnapshot]:
        """Return a registry entry when it is present in the snapshot."""

        for model in self.models:
            if model.model_id == model_id:
                return model
        return None
