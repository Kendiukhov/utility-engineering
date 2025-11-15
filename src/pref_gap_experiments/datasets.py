"""Utilities for loading scenario datasets from structured files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore

from .config import Scenario


@dataclass
class ScenarioDataset:
    """A collection of preference-gap scenarios."""

    scenarios: List[Scenario]

    @classmethod
    def from_file(cls, path: Path | str) -> "ScenarioDataset":
        path = Path(path)
        text = path.read_text()
        suffix = path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            if yaml is None:
                raise ModuleNotFoundError("PyYAML is required to load YAML scenario files")
            loaded = yaml.safe_load(text)
        elif suffix == ".json":
            loaded = json.loads(text)
        else:
            raise ValueError(f"Unsupported scenario file format: {path.suffix}")
        scenarios = [Scenario(**scenario) for scenario in loaded["scenarios"]]
        return cls(scenarios)

    @classmethod
    def from_yaml(cls, path: Path | str) -> "ScenarioDataset":
        """Backward-compatible YAML loader."""

        return cls.from_file(path)

    def __iter__(self) -> Iterator[Scenario]:
        return iter(self.scenarios)

    def identifiers(self) -> List[str]:
        return [scenario.identifier for scenario in self.scenarios]

    def extend(self, more: Iterable[Scenario]) -> None:
        self.scenarios.extend(more)
