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
├── experiment_config.json      # Example configuration referencing prompt strategies
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

3. Adjust `experiment_config.json` to list the strategies you wish to compare and
   configure global parameters (model name, temperature, etc.).

4. Run experiments with the CLI. By default a deterministic mock client is used
   so the harness can execute offline and in CI. To query an actual OpenAI model,
   pass `--use-openai` and ensure your environment is configured with an API key.
   When working without PyYAML installed, prefer JSON configuration files.

   ```bash
   PYTHONPATH=src python scripts/run_experiments.py data/scenarios.json experiment_config.json \
       --output reports.json

   You can provide deterministic scripted outputs for the mock client via
   `--mock-responses`. The repository includes `data/mock_responses.json`, which
   encodes multi-line prompt keys and responses for reproducing the comparisons in
   `analysis/results.md`:

   ```bash
   PYTHONPATH=src python scripts/run_experiments.py data/scenarios.json \
       configs/strategy_comparison.json \
       --mock-responses data/mock_responses.json \
       --output reports/strategy_comparison.json
   ```
   ```

5. Inspect the generated reports for per-scenario scores and average alignment
   metrics per strategy. Use these outputs to compare prompt engineering
   approaches and quantify improvements in revealed preference alignment. To
   produce a quick visualization of the results, run the helper script below.

   ```bash
   PYTHONPATH=src python analysis/plot_scores.py \
       --reports reports/strategy_comparison.json reports/global_values_override.json \
       --labels targeted global_override \
       --output analysis/figures/strategy_scores.svg
   ```

   The command writes an SVG bar chart that contrasts the average alignment
   score of each prompt strategy under two configuration regimes.

## Available prompt strategies

The repository currently includes five prompt-engineering strategies that can
be combined in experiment configurations:

- **baseline** – a plain helpful-assistant system prompt.
- **ranked_values** – injects a ranked list of scenario or globally supplied
  values into the system prompt.
- **safety_append** – appends reminders after each user query to reference the
  value order explicitly when responding.
- **value_checklist** – asks the assistant to walk through every value as a
  checklist before answering and to name the highest priority.
- **self_critique** – requires the assistant to identify the top value, answer
  normally, and then perform a short self-audit explaining how the leading
  value shaped the reply.

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
