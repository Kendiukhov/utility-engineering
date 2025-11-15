"""CLI for running preference gap experiments."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Dict

import json

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore

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
    parser.add_argument(
        "--mock-responses",
        type=Path,
        default=None,
        help=(
            "Optional path to a YAML or JSON file containing scripted responses for the mock client."
            " Ignored when --use-openai is provided."
        ),
    )
    return parser


def load_config(path: Path, scenarios: ScenarioDataset) -> ExperimentConfig:
    text = path.read_text()
    suffix = path.suffix.lower()
    if suffix == ".json":
        raw = json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise ModuleNotFoundError("PyYAML is required to load YAML config files")
        raw = yaml.safe_load(text)
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")
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


def load_mock_responses(path: Path | None) -> Dict[str, str]:
    if path is None:
        return {}
    text = path.read_text()
    suffix = path.suffix.lower()
    if suffix == ".json":
        raw = json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise ModuleNotFoundError("PyYAML is required to load YAML mock responses")
        raw = yaml.safe_load(text)
    else:
        raise ValueError(f"Unsupported mock responses format: {path.suffix}")
    if not isinstance(raw, dict):
        raise ValueError("Mock responses file must contain a mapping")
    # Support files that nest responses under a top-level key.
    if "responses" in raw and isinstance(raw["responses"], dict):
        raw = raw["responses"]
    return {str(key): str(value) for key, value in raw.items()}


def select_client(
    config: ExperimentConfig, use_openai: bool, mock_responses: Dict[str, str]
) -> MockLLMClient | OpenAIClient:
    if use_openai:
        if mock_responses:
            raise ValueError("Mock responses cannot be used with the OpenAI client")
        return OpenAIClient(model=config.llm_model)
    return MockLLMClient(model="mock", scripted_responses=mock_responses)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    scenarios = ScenarioDataset.from_file(args.dataset)
    config = load_config(args.config, scenarios)
    mock_responses = load_mock_responses(args.mock_responses)
    client = select_client(config, args.use_openai, mock_responses)
    runner = ExperimentRunner(config=config, client=client)
    reports = asyncio.run(runner.run())
    serialized: Dict[str, Dict[str, object]] = {name: report.to_dict() for name, report in reports.items()}
    suffix = args.output.suffix.lower()
    if suffix == ".json" or yaml is None:
        args.output.write_text(json.dumps(serialized, indent=2) + "\n")
    else:
        args.output.write_text(yaml.safe_dump(serialized))
    print(f"Wrote reports to {args.output}")


if __name__ == "__main__":
    main()
