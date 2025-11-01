"""Configuration dataclasses for preference gap experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Scenario:
    """Describes a scenario probing stated vs revealed value preferences."""

    identifier: str
    stated_preference_prompt: str
    conflict_prompt: str
    target_ranking: List[str]
    evaluation_instructions: str


@dataclass
class StrategyConfig:
    """Configuration for a prompt strategy."""

    name: str
    parameters: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExperimentConfig:
    """Holds all configuration required for an experiment run."""

    scenarios: List[Scenario]
    strategies: List[StrategyConfig]
    llm_model: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    parallelism: int = 4
    system_values: Optional[List[str]] = None

    def get_strategy_params(self, name: str) -> Dict[str, str]:
        for strategy in self.strategies:
            if strategy.name == name:
                return strategy.parameters
        raise KeyError(f"Strategy '{name}' not found in configuration")
