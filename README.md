# Preference Gap Experiment Harness

This repository implements a modular experimentation harness for studying the
stated versus revealed preference gap in large language models, inspired by the
empirical observations of Chiu et al. (2025) and the prompt engineering findings
of Liu et al. (2024).

## Project structure

```
.
├── data/
│   ├── scenarios.json          # Example scenarios probing value conflicts
│   └── scenarios.yaml          # YAML version (requires PyYAML to load)
├── experiment_config.yaml      # Example configuration referencing prompt strategies
├── scripts/
│   └── run_experiments.py      # CLI entry point for running studies
└── src/pref_gap_experiments/
    ├── config.py               # Dataclasses for experiment configuration
    ├── datasets.py             # Scenario loading utilities
    ├── evaluation.py           # Scoring and reporting helpers
    ├── experiments.py          # Experiment runner orchestrating LLM calls
    ├── llm.py                  # LLM client abstractions (OpenAI + mocks)
    ├── strategies.py           # Prompt-engineering strategies to evaluate
    └── __init__.py
```

## Getting started

1. (Optional) Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Review `data/scenarios.json` (or `scenarios.yaml` if you install PyYAML) and
   extend it with additional stated vs revealed preference probes derived from
   the literature or your own annotations.

3. Adjust `experiment_config.yaml` to list the strategies you wish to compare and
   configure global parameters (model name, temperature, etc.).

4. Run experiments with the CLI. By default a deterministic mock client is used
   so the harness can execute offline and in CI. To query an actual OpenAI model,
   pass `--use-openai` and ensure your environment is configured with an API key.

   ```bash
   python scripts/run_experiments.py data/scenarios.json experiment_config.yaml \
       --output reports.yaml
   ```

5. Inspect the generated `reports.yaml` for per-scenario scores and average
   alignment metrics per strategy. Use these outputs to compare prompt
   engineering approaches and quantify improvements in revealed preference
   alignment.

## Testing

Unit tests rely on the mock client to simulate model behavior:

```bash
pytest
```

## Extending the harness

- Implement new strategies by subclassing the `PromptStrategy` protocol in
  `src/pref_gap_experiments/strategies.py`.
- Integrate additional evaluation signals in `evaluation.py` to capture richer
  metrics (e.g., direct preference comparisons, contradiction detection).
- Swap in alternative LLM providers by implementing the `LLMClient` interface in
  `llm.py`.

These components enable systematic, scientific comparisons of prompt-engineering
techniques aimed at closing the declared vs revealed preference gap.
