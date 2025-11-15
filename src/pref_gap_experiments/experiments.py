"""Experiment runner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Type

from .config import ExperimentConfig, Scenario
from .evaluation import AlignmentReport, AlignmentResult, score_conflict_response
from .llm import LLMClient, gather_with_concurrency
from .strategies import (
    BaselinePromptStrategy,
    PromptStrategy,
    RankedValuesPromptStrategy,
    SafetyAppendPromptStrategy,
)

STRATEGY_REGISTRY: Dict[str, Type[PromptStrategy]] = {
    "baseline": BaselinePromptStrategy,
    "ranked_values": RankedValuesPromptStrategy,
    "safety_append": SafetyAppendPromptStrategy,
}


@dataclass
class ExperimentRunner:
    """Coordinates experiment execution for multiple strategies."""

    config: ExperimentConfig
    client: LLMClient

    async def run(self) -> Dict[str, AlignmentReport]:
        reports: Dict[str, AlignmentReport] = {}
        for strategy_config in self.config.strategies:
            strategy = self._instantiate_strategy(strategy_config.name, strategy_config.parameters)
            results = await self._run_strategy(strategy)
            reports[strategy.name] = AlignmentReport(results)
        return reports

    async def _run_strategy(self, strategy: PromptStrategy) -> List[AlignmentResult]:
        prompts = [strategy.build_prompts(scenario, self.config.system_values) for scenario in self.config.scenarios]
        coroutines = []
        for scenario, prompt_pack in zip(self.config.scenarios, prompts, strict=True):
            coroutines.append(
                self._evaluate_scenario(
                    scenario,
                    prompt_pack,
                )
            )
        return await gather_with_concurrency(self.config.parallelism, coroutines)

    async def _evaluate_scenario(
        self, scenario: Scenario, prompt_pack: Dict[str, str]
    ) -> AlignmentResult:
        system_prompt = prompt_pack["system"]
        stated_response = await self.client.generate(
            system=system_prompt,
            prompt=prompt_pack["stated_query"],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        conflict_response = await self.client.generate(
            system=system_prompt,
            prompt=prompt_pack["conflict_query"],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return score_conflict_response(
            scenario,
            stated_response=stated_response,
            conflict_response=conflict_response,
            evaluation_notes={"system_prompt": system_prompt},
        )

    def _instantiate_strategy(self, name: str, params: Dict[str, str]) -> PromptStrategy:
        if name not in STRATEGY_REGISTRY:
            raise KeyError(f"Unknown strategy '{name}'")
        return STRATEGY_REGISTRY[name](**params)
