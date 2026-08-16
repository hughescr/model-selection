---
name: model-selection
description: Select and compare language models using Artificial Analysis benchmark scores, pricing, speed, and task fit. Use for explicit comparisons; new or uncertain model or effort choices; runtime alias or availability uncertainty; tasks outside a stable local routing table; repeated routing or telemetry underperformance; or periodic calibration. Do not invoke for routine Claude Agent or Workflow spawns already covered by the local table. Preserve an explicit user model or effort choice unless it is unavailable.
---

# Model Selection

Use the bundled Python client to discover local runtime options, fetch the Artificial Analysis LLM catalog with disk caching, rank models by task-relevant benchmarks, and format decision-relevant evidence.

## Fast path and slow path

For a routine Claude Agent or Workflow spawn covered by the stable local routing table, select that route directly: do not discover, fetch, rank, or consult Artificial Analysis. Take the slow path only for the triggers in the description. An explicit user model or effort selection wins, subject to runtime availability.

## Slow-path workflow

1. Discover only the affected runtime when availability, an alias, or an explicit selection is unresolved:

   ```bash
   python3 scripts/model_selection.py discover --runtime claude --format markdown
   ```

   Codex discovery reads `CODEX_HOME/models_cache.json` and `config.toml`. Treat entries with `visibility: list` as available and mark hidden entries separately. Claude Code discovery reads `~/.claude/settings.json`, observed model fields in `~/.claude.json`, and the installed CLI help. Claude's `opus`, `sonnet`, and `haiku` names are aliases, not proof that every dated model is enabled for the account. There is no supported Claude Code command that enumerates the full entitlement set; preserve that uncertainty in the recommendation.

2. Fetch the model catalog only if discovery does not resolve the decision. The default credentials file is `creds.json` beside this skill, and the default cache is `.cache/llms-models.json`.

   ```bash
   python3 scripts/model_selection.py fetch
   python3 scripts/model_selection.py fetch --refresh
   ```

   Use `ARTIFICIAL_ANALYSIS_API_KEY` or `--credentials PATH` when the key is stored elsewhere. Never print, commit, or place the key in generated markdown. The client uses a 24-hour cache by default and falls back to stale data after a failed refresh; use `--no-stale-if-error` when freshness is a hard requirement.

3. Rank only if the decision remains unresolved. Prefer an Artificial Analysis category index when present; otherwise the client uses the available benchmark fields in the topic alias list and reports the fields used.

   ```bash
   python3 scripts/model_selection.py rank --topic coding --runtime all --format markdown
   python3 scripts/model_selection.py rank --topic writing --sort score --format markdown
   python3 scripts/model_selection.py rank --metric livecodebench --format table
   python3 scripts/model_selection.py rank --topic coding --available-only --runtime codex
   python3 scripts/model_selection.py rank --topic general --sort cost-per-intelligence --format markdown
   ```

4. Inspect a full benchmark breakdown only when it is needed to resolve a close or consequential choice:

   ```bash
   python3 scripts/model_selection.py rank --topic coding --metrics all --format json > /tmp/models-coding.json
   python3 scripts/model_selection.py rank --topic coding --metrics livecodebench,scicode,terminal_bench_v2_1 --format markdown
   ```

   Load the relevant topic reference before interpreting a score. References are deliberately split by capability: [coding](references/benchmarks-coding.md), [writing and knowledge work](references/benchmarks-writing-knowledge.md), [math and science](references/benchmarks-math-science.md), and [agents, instruction following, and cross-cutting caveats](references/benchmarks-agents-reasoning.md). Read [Artificial Analysis API](references/artificial-analysis-api.md) for field semantics and cache behavior.

5. Report a shortlist, not a single universal winner. By default, include availability, one task-relevant score and source field, and price; include speed only when latency matters. The catalog may return full records, but analyze and report only decision-relevant fields. Call out missing metrics, standalone versus index benchmarks, confidence intervals when available, and whether the score is model-only or agent/harness-dependent.

## Cost Per Intelligence

Artificial Analysis API prices and benchmark `cost_per_task` values are API-comparison inputs, not Claude Max quota weights or a conversion to a weekly allowance. Use observed account meters and task telemetry for account usage; state the result as unknown when it is unpublished.

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
