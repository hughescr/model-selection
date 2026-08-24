---
name: model-selection
description: Select and compare language models using Artificial Analysis benchmark scores, pricing, speed, and task fit. Use for explicit comparisons; new or uncertain model or effort choices; runtime alias or availability uncertainty; tasks outside a stable local routing table; repeated routing or telemetry underperformance; or periodic calibration. Do not invoke for routine Agent or Workflow spawns already covered by the local table, including cross-family verification pairings the table already names. Preserve an explicit user model or effort choice unless it is unavailable.
---

# Model Selection

Use the bundled Python client to discover local runtime options, fetch the Artificial Analysis LLM catalog with disk caching, rank models by task-relevant benchmarks, and format decision-relevant evidence.

## Fast path and slow path

For a routine Agent or Workflow spawn covered by the stable local routing table, select that route directly: do not discover, fetch, rank, or consult Artificial Analysis. This includes picking a cross-family challenger from the pairings below — that is a table lookup, not a slow-path decision. Take the slow path only for the triggers in the description. An explicit user model or effort selection wins, subject to runtime availability.

## Local gateway routes

The `gpt-*` rows of the local routing table reach OpenAI models over the `utraque` proxy on `127.0.0.1:8317`, billed to the Codex subscription rather than the Anthropic account. Route agents live in `~/.claude/agents/` alongside the Claude routes; this skill's `agents/` directory holds a Codex interface manifest for the skill itself and is not a route directory. Do not define route agents here.

"Route effort" is what the route actually runs at, and it is carried by the suffixed model
name the agent file sends — not by the frontmatter `effort` key. "Proxy default" is what
the same model would run at if it were named bare, which is why the suffix is mandatory.

| Route | Model name sent | Use for | Peer Claude route | Route effort | Proxy default if named bare | Supported efforts | Confidence |
|---|---|---|---|---|---|---|---|
| `gpt-sol-high`, `gpt-sol-xhigh` | `sol-high`, `sol-xhigh` (`gpt-5.6-sol`) | Heavy work, consequential review, complex debugging, long-horizon agent runs. | `opus-high` | `high`, `xhigh` | `low` | `low`-`ultra` | Strong: peer on both the intelligence index and the role. |
| `gpt-sol-medium` | `sol-medium` | Routine verification, or a second opinion on another agent's work. | `opus-medium` | `medium` | `low` | `low`-`ultra` | Inferred from role, not from a measured head-to-head. |
| `gpt-terra-medium`, `gpt-terra-high` | `terra-medium`, `terra-high` (`gpt-5.6-terra`) | Normal substantive execution; the default GPT leaf. Use `high` for multi-file changes. | `sonnet-high` | `medium`, `high` | `medium` | `low`-`ultra` | Strong on positioning: terra scores within 1.4 coding points of sol at under half the cost. |
| `gpt-luna-medium` | `luna-medium` (`gpt-5.6-luna`) | Bounded work with objective checks: extraction, classification, mechanical refactors. Short inputs only. | `sonnet-medium` | `medium` | `medium` | `low`-`max` | Strong on positioning and on the long-context limit; the peering is a cost-and-role match. |
| `gpt-luna-low` | `luna-low` | Cheap mechanical work and summaries. | `haiku-summary`, `haiku-basic` | `low` | `medium` | `low`-`max` | Weak: no published head-to-head against Haiku, and the index puts luna well above it. A cost peer, not a capability peer. |
| `gpt-spark-high` | `spark-high` (`gpt-5.3-codex-spark`) | Tight edit-test-lint loops and executing a written checklist, at roughly ten times the throughput of a reasoning model. Never planning, review, or long jobs. | None. Speed peer of `haiku-basic`, coding-accuracy peer of `sonnet-medium`. | `high` | `high` | `low`-`xhigh` | Speed and limits are well sourced; the peering is inference. |

Facts that constrain these routes:

- **Context is 272k tokens, not the 1M the API docs advertise** — 128k for `gpt-spark-high`, which fills in about two minutes at its throughput. Never plan a larger task onto a `gpt-*` route.
- **Keep luna off long context entirely.** Its long-context recall is 41.3% against sol's 91.5%, so it degrades quietly rather than failing.
- **A suffixed model name is the only way to set effort.** Frontmatter `effort` never reaches the proxy: utraque's `chooseEffort` takes a model-name suffix, then two `Options` fields that no non-test code assigns, then the catalog default — there is no request field an Anthropic-shaped client can set. So the agent files send `sol-high`, `terra-medium` and so on, and the frontmatter `effort` key is bookkeeping that satisfies the CLAUDE.md pin rule. If a route is ever changed to a bare alias it silently drops to the proxy default — `low` for sol, which is the worst case on a consequential-review route.
- **`ultra` is not a valid frontmatter effort.** Reach it only through a suffixed model name (`sol-ultra`), and expect roughly triple the cost for one to three points. OpenAI documents `ultra` as sol-only; the live catalog also accepts it on terra, which no public source confirms.
- The proxy accepts a bare alias (`sol`), a pinned name (`sol-5.6`), a raw slug (`gpt-5.6-sol`), or an effort suffix (`sol-high`); the model picker shows the same models as `anthropic-compat.<alias>`.
- **Do not route to `gpt-5.5`, `gpt-5.4`, or `gpt-5.4-mini`** — all retire on 2026-08-31, and OpenAI's own migration advice is terra and luna. Do not route to `codex-auto-review`: it is hidden and undocumented.

These routes are reachable only when `env.ANTHROPIC_BASE_URL` in `~/.claude/settings.json` names the proxy. That key is not set by default: check it before selecting a `gpt-*` route, because without it the model name goes to `api.anthropic.com` and is rejected as unknown. See `~/.claude/UTRAQUE-SETTINGS-DELTA.md`.

For availability, prefer the proxy's own state over the discovery step below: `GET /healthz` reports Codex auth state, catalog state and model count, transport kind, and quota. The live catalog is the authority on which models and efforts exist. When the proxy is down, every `gpt-*` route fails immediately and the Claude routes are unaffected.

## Cross-family verification

Verify across families. A same-family reviewer shares the proposer's blind spots, so first-party work by a Claude model is verified or challenged by a GPT model, and first-party work by a GPT model is verified or challenged by a Claude model. No model reviews its own output, and no family is the only reviewer of its own work.

| Proposer | Challenger | Escalate to |
|---|---|---|
| `opus-high`, `fable-*` | `gpt-sol-high` | `gpt-sol-xhigh` |
| `opus-medium` | `gpt-sol-medium` | `gpt-sol-high` |
| `sonnet-high` | `gpt-terra-high` | `gpt-sol-medium` |
| `sonnet-medium` | `gpt-luna-medium` | `gpt-terra-high` |
| `haiku-summary`, `haiku-basic` | `gpt-luna-low` | `gpt-luna-medium` |
| `gpt-sol-high`, `gpt-sol-xhigh` | `opus-high` | `fable-high` |
| `gpt-sol-medium` | `opus-medium` | `opus-high` |
| `gpt-terra-medium`, `gpt-terra-high` | `sonnet-high` | `opus-medium` |
| `gpt-luna-*`, `gpt-spark-high` | `sonnet-medium` | `sonnet-high` |

Size the challenger to the cost of being wrong, not to the proposer's rank. Treat a cross-family disagreement as a finding to resolve, not a tie to split: escalate one rung and report both positions. `gpt-spark-high` proposes and executes but never reviews.

This table is the authority for choosing the single verifier in the review-changes skill: take the session's own model as the proposer and read off the challenger. That verifier is advised for substantial changes, not required for every change.

When the proxy is unavailable — not configured, or configured and down — no cross-family route exists. Fall back to a stronger same-family route and state in the report that the verification was same-family. The proxy authenticates with the Codex subscription credential, so a stale credential is fixed with `codex login`, not by rerouting.

## Slow-path workflow

1. Discover only the affected runtime when availability, an alias, or an explicit selection is unresolved:

   ```bash
   python3 scripts/model_selection.py discover --runtime claude --format markdown
   ```

   Codex discovery reads `CODEX_HOME/models_cache.json` and `config.toml`. Treat entries with `visibility: list` as available and mark hidden entries separately. Claude Code discovery reads `~/.claude/settings.json`, observed model fields in `~/.claude.json`, and the installed CLI help. Claude's `opus`, `sonnet`, and `haiku` names are aliases, not proof that every dated model is enabled for the account. There is no supported Claude Code command that enumerates the full entitlement set; preserve that uncertainty in the recommendation. Neither runtime file knows about the gateway: when Claude Code is pointed at `utraque`, the Codex models are reachable from inside Claude Code as well, and the proxy's `/healthz` is the authority on which of them are live.

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
- Choose a reviewer or challenger by family first and rank second. Take the pairing from the cross-family table above; a same-family review is a weaker signal at the same price.
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
