"""Experiment harness for studying stated vs revealed preference gaps in LLMs."""

from .config import ExperimentConfig, Scenario, StrategyConfig
from .datasets import ScenarioDataset
from .evaluation import AlignmentReport, compute_alignment_gap
from .experiments import ExperimentRunner
from .llm import LLMClient, MockLLMClient
from .strategies import (
    BaselinePromptStrategy,
    PromptStrategy,
    RankedValuesPromptStrategy,
    SafetyAppendPromptStrategy,
)

__all__ = [
    "AlignmentReport",
    "BaselinePromptStrategy",
    "ExperimentConfig",
    "ExperimentRunner",
    "LLMClient",
    "MockLLMClient",
    "PromptStrategy",
    "RankedValuesPromptStrategy",
    "SafetyAppendPromptStrategy",
    "Scenario",
    "ScenarioDataset",
    "StrategyConfig",
    "compute_alignment_gap",
]
