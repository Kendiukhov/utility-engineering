# Prompt Strategy Comparisons

This is a summary of what we learned by running the scripted
experiments. The accompanying bar chart shows how each strategy performed when
we used scenario-specific values versus when we forced a global value list.

![Average alignment scores for each strategy under both configurations.](figures/strategy_scores.svg)

## Configuration A – Scenario-Specific Rankings

- **Config file:** `configs/strategy_comparison.json`
- **Report:** `reports/strategy_comparison.json`

| Strategy         | Average Score | What happened in simple words |
|------------------|---------------|--------------------------------|
| baseline         | 0.25          | The assistant chased popularity and convenience, never repeating the stated value order. |
| ranked_values    | 0.94          | Adding the ranked list to the system prompt pushed the assistant to mention almost every target value when resolving the conflict. |
| safety_append    | 0.94          | Short reminders after each user message had the same effect as the system-level value list. |
| value_checklist  | 1.00          | Listing every value before answering guaranteed the assistant reused the full priority order. |
| self_critique    | 0.83          | Asking for a self-check helped, but because it focused on the top value, the assistant still skipped some lower-ranked values.【F:reports/strategy_comparison.json†L1-L93】

**Takeaway.** Any prompt that explicitly rehearses the scenario’s own value
ordering keeps the model’s conflict-time response aligned. Forcing the assistant
to restate the values (checklist) was the strongest option, while the lighter
self-critique only partially closed the gap.

## Configuration B – Global Value Override

- **Config file:** `configs/global_values_override.json`
- **Report:** `reports/global_values_override.json`

| Strategy         | Average Score | What happened in simple words |
|------------------|---------------|--------------------------------|
| baseline         | 0.25          | No change: the plain prompt still ignores the target values. |
| ranked_values    | 0.25          | Overriding the system prompt with unrelated values (“Honesty, Compassion, Compliance”) erased the gains from the ranked strategy. |
| safety_append    | 0.94          | Because the reminders still cite the scenario terms, the assistant stayed faithful to the original ranking. |
| value_checklist  | 0.38          | The checklist now walks through the wrong value list, so alignment drops sharply. |
| self_critique    | 0.25          | The self-audit talks only about the injected global values and ignores the scenario priorities entirely.【F:reports/global_values_override.json†L1-L89】

**Takeaway.** Prompt engineering only helps when the value inventory matches the
scenario. Global overrides that quote the wrong values undo the improvements of
structured prompting, while strategies that repeat the original scenario wording
remain resilient.
