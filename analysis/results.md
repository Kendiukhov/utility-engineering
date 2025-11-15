# Prompt Strategy Comparisons

This document summarizes two offline experiment configurations that explore how
prompt engineering affects revealed-value alignment when the underlying model
outputs are controlled via the scripted mock client.

## Configuration A: Scenario-Specific Value Rankings

- **Config file:** `configs/strategy_comparison.json`
- **Responses:** `data/mock_responses.json`
- **Report:** `reports/strategy_comparison.json`

| Strategy        | Average Score | Notable Behavior |
|-----------------|---------------|------------------|
| baseline        | 0.25          | Echoes popularity and convenience pressures without referencing the stated priority order, leading to minimal value mentions. |
| ranked_values   | 0.94          | Injecting the scenario-specific ranked values raises the proportion of explicit value references in both stated and conflict responses. |
| safety_append   | 0.94          | Reminder text appended to each prompt reinforces transparency and safety cues, matching the performance of the ranked-value system prompt. |

**Observation.** Both structured prompting approaches dramatically reduce the
revealed-preference gap relative to the baseline by ensuring that conflict
responses reuse the priority values articulated in the stated preference
prompts.【F:reports/strategy_comparison.json†L1-L57】

## Configuration B: Global Value Override

- **Config file:** `configs/global_values_override.json`
- **Responses:** `data/mock_responses.json`
- **Report:** `reports/global_values_override.json`

| Strategy        | Average Score | Notable Behavior |
|-----------------|---------------|------------------|
| baseline        | 0.25          | Unchanged from Configuration A because the baseline system prompt ignores the global value override. |
| ranked_values   | 0.25          | The injected global ordering (“Honesty, Compassion, Compliance”) fails to mention scenario-specific priorities, so alignment collapses to baseline levels. |
| safety_append   | 0.94          | Reminders still reference the original ranking terms inside the prompts, preserving the high alignment seen in Configuration A. |

**Observation.** Overriding the ranked-value system prompt with a generic set of
values erases the improvement delivered by the ranked-values strategy, showing
that mismatched value inventories can undo stated-versus-revealed preference
gains. The reminder-based strategy remains robust because it continues to quote
scenario-specific values inside the user prompts.
