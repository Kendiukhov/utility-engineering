"""CLI for running preference gap experiments."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Dict

import yaml

from pref_gap_experiments import (
    ExperimentConfig,
    ExperimentRunner,
    MockLLMClient,
    ScenarioDataset,
    StrategyConfig,
)
from pref_gap_experiments.llm import OpenAIClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Path to dataset JSON or YAML file")
    parser.add_argument("config", type=Path, help="Path to experiment configuration YAML file")
    parser.add_argument("--use-openai", action="store_true", help="Use the OpenAI API client")
    parser.add_argument("--output", type=Path, default=Path("reports.yaml"), help="Where to write the report")
    return parser


def load_config(path: Path, scenarios: ScenarioDataset) -> ExperimentConfig:
    raw = yaml.safe_load(path.read_text())
    strategies = [StrategyConfig(**entry) for entry in raw["strategies"]]
    return ExperimentConfig(
        scenarios=list(scenarios),
        strategies=strategies,
        llm_model=raw["llm_model"],
        temperature=raw.get("temperature", 0.0),
        max_tokens=raw.get("max_tokens"),
        parallelism=raw.get("parallelism", 4),
        system_values=raw.get("system_values"),
    )


def select_client(config: ExperimentConfig, use_openai: bool) -> MockLLMClient | OpenAIClient:
    if use_openai:
        return OpenAIClient(model=config.llm_model)
    return MockLLMClient(model="mock", scripted_responses={})


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    scenarios = ScenarioDataset.from_file(args.dataset)
    config = load_config(args.config, scenarios)
    client = select_client(config, args.use_openai)
    runner = ExperimentRunner(config=config, client=client)
    reports = asyncio.run(runner.run())
    serialized: Dict[str, Dict[str, object]] = {name: report.to_dict() for name, report in reports.items()}
    args.output.write_text(yaml.safe_dump(serialized))
    print(f"Wrote reports to {args.output}")


if __name__ == "__main__":
    main()
