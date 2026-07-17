---
name: model-selection
description: Select and compare language models using Artificial Analysis benchmark scores, pricing, speed, and task fit. Use when choosing a model for coding, writing, knowledge work, agents, math, science, reasoning, multilingual, or multimodal tasks; when comparing cost per intelligence; or when determining which model names and aliases are available in the current Codex or Claude Code runtime.
---

# Model Selection

Use the bundled Python client to discover local runtime options, fetch the Artificial Analysis LLM catalog with disk caching, rank models by task-relevant benchmarks, and format the complete evaluation payload for inspection.

## Workflow

1. Discover what the current host can invoke before ranking anything:

   ```bash
   python3 scripts/model_selection.py discover --runtime all --format markdown
   ```

   Codex discovery reads `CODEX_HOME/models_cache.json` and `config.toml`. Treat entries with `visibility: list` as available and mark hidden entries separately. Claude Code discovery reads `~/.claude/settings.json`, observed model fields in `~/.claude.json`, and the installed CLI help. Claude's `opus`, `sonnet`, and `haiku` names are aliases, not proof that every dated model is enabled for the account. There is no supported Claude Code command that enumerates the full entitlement set; preserve that uncertainty in the recommendation.

2. Fetch the model catalog. The default credentials file is `creds.json` beside this skill, and the default cache is `.cache/llms-models.json`.

   ```bash
   python3 scripts/model_selection.py fetch
   python3 scripts/model_selection.py fetch --refresh
   ```

   Use `ARTIFICIAL_ANALYSIS_API_KEY` or `--credentials PATH` when the key is stored elsewhere. Never print, commit, or place the key in generated markdown. The client uses a 24-hour cache by default and falls back to stale data after a failed refresh; use `--no-stale-if-error` when freshness is a hard requirement.

3. Rank by the task. Prefer an Artificial Analysis category index when present; otherwise the client uses the available benchmark fields in the topic alias list and reports the fields used.

   ```bash
   python3 scripts/model_selection.py rank --topic coding --runtime all --format markdown
   python3 scripts/model_selection.py rank --topic writing --sort score --format markdown
   python3 scripts/model_selection.py rank --metric livecodebench --format table
   python3 scripts/model_selection.py rank --topic coding --available-only --runtime codex
   python3 scripts/model_selection.py rank --topic general --sort cost-per-intelligence --format markdown
   ```

4. Inspect the full benchmark breakdown before making a recommendation:

   ```bash
   python3 scripts/model_selection.py rank --topic coding --metrics all --format json > /tmp/models-coding.json
   python3 scripts/model_selection.py rank --topic coding --metrics livecodebench,scicode,terminal_bench_v2_1 --format markdown
   ```

   Load the relevant topic reference before interpreting a score. References are deliberately split by capability: [coding](references/benchmarks-coding.md), [writing and knowledge work](references/benchmarks-writing-knowledge.md), [math and science](references/benchmarks-math-science.md), and [agents, instruction following, and cross-cutting caveats](references/benchmarks-agents-reasoning.md). Read [Artificial Analysis API](references/artificial-analysis-api.md) for field semantics and cache behavior.

5. Report a shortlist, not a single universal winner. Include model identity, runtime availability evidence, benchmark score and source field, price, speed, score coverage, and the reason the selected benchmark matches the task. Call out missing metrics, standalone versus index benchmarks, confidence intervals when available, and whether the score is model-only or agent/harness-dependent.

## Cost Per Intelligence

Use `cost_per_intelligence_point = blended_price_per_1m_tokens / selected_score`, where the score is on a 0-100 scale. Also show `cost_per_100_intelligence_points`, which is easier to read. This is a normalized value for comparing models under the same rough token mix, not the expected price of a real user task. Real task cost depends on prompt length, output length, reasoning tokens, cache hits, provider endpoint, tool calls, and harness retries.

The free endpoint's `price_1m_blended_3_to_1` is used as reported. If it is absent, the helper falls back to `(input_price + 3 * output_price) / 4`. Do not silently compare this ratio with a benchmark score from a different evaluation family without labeling the denominator.

## Selection Rules

- Match the benchmark to the work. Coding index is a useful first sort for code, but terminal execution, repository repair, scientific Python, and code completion are different skills.
- Treat composite indices as summaries, not ground truth. Preserve per-benchmark rows and prefer a task-specific benchmark when one exists.
- Do not treat writing quality as a pure scalar. GDPval and Briefcase involve deliverables and knowledge work; IFBench measures instruction compliance; neither fully captures voice, originality, factual editing, or audience fit.
- Prefer fresh or decontaminated evaluations when models are close. Static benchmark scores can be inflated by training-data overlap, prompt sensitivity, grader choice, or harness differences.
- Avoid mixing raw percentages, Elo ratings, and index values as if they share the same meaning. The formatter normalizes 0-1 pass rates to display percentages but retains the original raw values in JSON.
- When no local runtime match exists, distinguish “best in the catalog” from “invokable here.” A model may be benchmarked by Artificial Analysis without being selectable in the current agent product.
- Cite Artificial Analysis when sharing data from the free API. The API documentation requires attribution.

## Python API

The script is importable for custom formatting. Keep network access and caching in the helper rather than duplicating requests:

```python
from pathlib import Path
from scripts.model_selection import enrich_models, fetch_models, payload_data

payload, cache_info = fetch_models(cache_dir=Path(".cache"))
rows = enrich_models(payload_data(payload), topic="coding")
for row in rows[:10]:
    print(row["name"], row["selected_score"], row["cost_per_100_intelligence_points"])
```

Use `clean_for_json`, `markdown`, or `table` from the module for downstream formatting. Keep the raw `evaluations` and `pricing` objects in exported data so future topic references can be applied without a new API call.

## Resources

- [Artificial Analysis API](references/artificial-analysis-api.md): local Markdown transcription of the free endpoint contract, fields, errors, attribution, and cache rules.
- [Coding benchmarks](references/benchmarks-coding.md): Terminal-Bench, SciCode, LiveCodeBench, SWE-bench, and coding-index interpretation.
- [Writing and knowledge work](references/benchmarks-writing-knowledge.md): GDPval, AA-Briefcase, AA-LCR, AA-Omniscience, IFBench, and MMLU-Pro.
- [Math and science](references/benchmarks-math-science.md): HLE, GPQA Diamond, CritPt, MATH-500, AIME, and science/coding crossover.
- [Agents and reasoning](references/benchmarks-agents-reasoning.md): tau-style tool use, composite-index weighting, grader and contamination risks, and practical decision heuristics.
