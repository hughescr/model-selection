---
name: model-selection
description: Compare language models on Artificial Analysis benchmarks, price, speed, and task fit. Use for explicit comparisons, uncertain model or effort choices, alias or availability questions, work outside the CLAUDE.md routing table, or periodic calibration. Not for routine spawns the table already covers, including cross-family pairings. An explicit user choice wins unless unavailable.
---

# Model Selection

A bundled Python client discovers local runtime options, fetches the Artificial Analysis LLM catalog with disk caching, ranks models by task-relevant benchmarks, and formats the evidence.

## Fast path first

For a routine spawn covered by the routing table in `~/.claude/CLAUDE.md`, select that route and stop — no discovery, fetch, or ranking. Picking a cross-family challenger from the table below is also a lookup, not a slow-path decision. Take the slow path only for the triggers in the description. An explicit user selection wins, subject to availability.

## Local gateway routes

The `gpt-*` routes reach OpenAI models over the `utraque` proxy on `127.0.0.1:8317`, billed to the Codex subscription. The `deepseek-*` routes reach DeepSeek's Anthropic-compatible endpoint over the same proxy and spend a prepaid DeepSeek API balance, so they are the only metered routes. Route agents live in `~/.claude/agents/`; this skill's `agents/` directory is a Codex interface manifest, not a route directory — do not define routes here.

"Route effort" is what the route actually runs at. On the Codex leg it is carried by the suffixed model name the agent file sends, not by the frontmatter `effort` key; on the DeepSeek leg it is the frontmatter `effort` key, which Claude Code sends as the request's effort field and the proxy forwards. "Proxy default" is what the same model runs at if named bare.

| Route | Model name sent | Use for | Peer Claude route | Route effort | Proxy default if named bare | Supported efforts | Confidence |
|---|---|---|---|---|---|---|---|
| `gpt-astra-medium`, `gpt-astra-high`, `gpt-astra-xhigh` | `astra-medium`, `astra-high`, `astra-xhigh` (`gpt-6-astra`) | Consequential challenge above sol, and work sol stalled on. | `fable-high`, `fable-xhigh` | `medium`, `high`, `xhigh` | unknown | unknown until the catalog lists it | Index position is strong (see snapshot); supported efforts, proxy default, and context window are unverified because the backend is not yet live. |
| `gpt-sol-high`, `gpt-sol-xhigh` | `sol-high`, `sol-xhigh` (`gpt-5.6-sol`) | Heavy work, consequential review, complex debugging, long-horizon agent runs. | `opus-high` | `high`, `xhigh` | `low` | `low`-`ultra` | Strong: peer on both the intelligence index and the role. |
| `gpt-sol-medium` | `sol-medium` | Routine verification, or a second opinion on another agent's work. | `opus-medium` | `medium` | `low` | `low`-`ultra` | Inferred from role, not from a measured head-to-head. |
| `gpt-terra-medium`, `gpt-terra-high` | `terra-medium`, `terra-high` (`gpt-5.6-terra`) | Normal substantive execution; the default GPT leaf. Use `high` for multi-file changes. | `sonnet-high` | `medium`, `high` | `medium` | `low`-`ultra` | Strong on positioning: terra scores within 1.4 coding points of sol at under half the cost. |
| `gpt-luna-medium` | `luna-medium` (`gpt-5.6-luna`) | Bounded work with objective checks: extraction, classification, mechanical refactors. Short inputs only. | `sonnet-medium` | `medium` | `medium` | `low`-`max` | Strong on positioning and on the long-context limit; the peering is a cost-and-role match. |
| `gpt-luna-low` | `luna-low` | Cheap mechanical work and summaries. | `haiku-summary`, `haiku-basic` | `low` | `medium` | `low`-`max` | Weak: no published head-to-head against Haiku, and the index puts luna well above it. A cost peer, not a capability peer. |
| `deepseek-flash-low`, `deepseek-flash-medium`, `deepseek-flash-high` | `deepseek-flash` (DeepSeek V4.1 Flash) plus frontmatter effort | The default DeepSeek route and the cheapest third-family challenger; peers Haiku, `sonnet-medium`, and `sonnet-high` by tier. | `haiku-*`, `sonnet-medium`, `sonnet-high` | `low`, `medium`, `high` | DeepSeek's own default | forwarded unvalidated; `low`-`high` exercised | Index position is strong; the per-tier peering is inferred from the single max-effort point AA publishes. |
| `deepseek-v4-pro-low`, `deepseek-v4-pro-medium`, `deepseek-v4-pro-high` | `deepseek-v4-pro` (DeepSeek V4 Pro 0813) plus frontmatter effort | Only when a task needs something the index does not measure; on the index Flash dominates it. No image input. | `sonnet-medium`, `opus-medium`, `opus-high` | `low`, `medium`, `high` | DeepSeek's own default | forwarded unvalidated; `low`-`high` exercised | The peering is a role placeholder, not evidence: AA puts Pro below Flash at over twice the cost. |

Facts that constrain these routes:

- **Context is 272k tokens on the Codex leg, not the 1M the API docs advertise.** Never plan a larger task onto a `gpt-*` route. DeepSeek and astra windows are unverified.
- **Keep luna off long context.** Its long-context recall is 41.3% against sol's 91.5%, so it degrades quietly rather than failing.
- **On the Codex leg a suffixed model name is the only way to set effort.** Frontmatter `effort` never reaches that leg: utraque's `chooseEffort` reads a model-name suffix, then two `Options` fields no non-test code assigns, then the catalog default. So agent files send `sol-high`, `terra-medium`, and the frontmatter `effort` key is bookkeeping for the CLAUDE.md pin rule. A bare alias silently drops to the proxy default — `low` for sol, the worst case on a consequential-review route.
- **On the DeepSeek leg the model name must be exact** (`deepseek-flash`, `deepseek-v4-pro`; a suffix like `deepseek-flash-high` is rejected as unrecognised) and effort travels in the frontmatter key instead. The proxy forwards the effort field as-is, so a value DeepSeek does not honor fails or degrades upstream rather than at the proxy.
- **`ultra` is not a valid frontmatter effort.** Reach it only via a suffixed name (`sol-ultra`), at roughly triple the cost for one to three points. OpenAI documents `ultra` as sol-only; the live catalog also accepts it on terra, which no public source confirms.
- The proxy accepts a bare alias (`sol`), a pinned name (`sol-5.6`), a raw slug (`gpt-5.6-sol`), or an effort suffix (`sol-high`); the model picker shows these as `anthropic-compat.<alias>`.
- **Do not route to `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, or `gpt-5.3-codex-spark`.** The first three retire 2026-08-31 and OpenAI's migration advice is terra and luna; spark is excluded by choice and its agent was removed 2026-09-11. Do not route to `codex-auto-review`: hidden and undocumented.

These routes work only when `ANTHROPIC_BASE_URL` names the proxy. The `claude` alias (`claude-smart.sh`) sets it at launch when the proxy answers healthy, so check the environment variable, not `settings.json`. Without it the model name reaches `api.anthropic.com` and is rejected. See `~/.claude/UTRAQUE-SETTINGS-DELTA.md`.

For availability prefer the proxy's own state: `GET /healthz` reports Codex auth, catalog state and model count, transport, and quota, and `GET /v1/models` lists what is routable now. The live catalog is the authority on which models and efforts exist; DeepSeek rows appear only when a DeepSeek key is configured. When the proxy is down every `gpt-*` and `deepseek-*` route fails immediately; Claude routes are unaffected.

### Intelligence-cost snapshot

Artificial Analysis Intelligence Index against cost per index task, read from the 2026-09-11 chart. Values are approximate chart readings, not API fields; AA's "medium" and "max" are its own effort settings, not this table's tiers. Cost is metered only on the DeepSeek leg; for the two subscription legs treat it as a quota-burn proxy.

| Model (AA effort) | Index | Cost/task | On Pareto line |
|---|---|---|---|
| Claude Fable 5.1 (max with fallback) | 53 | $8 | no |
| GPT-6 Astra (max) | 53 | $3.2 | yes |
| Claude Opus 5 (max) | 51 | $6 | no |
| GPT-6 Astra (medium) | 50 | $1.25 | yes |
| Claude Fable 5.1 (medium with fallback) | 49 | $3.2 | no |
| GPT-5.6 Sol (max) | 47 | $2.1 | no |
| Claude Opus 5 (medium) | 45 | $2.3 | no |
| GPT-5.6 Terra (max) | 42 | $1.4 | no |
| GPT-5.6 Sol (medium) | 39.5 | $0.5 | no |
| DeepSeek V4.1 Flash (max) | 39.5 | $0.28 | no, just under |
| GPT-5.6 Luna (max) | 37.5 | $0.19 | yes |
| DeepSeek V4 Pro 0813 (max) | 36 | $0.68 | no |
| GPT-5.6 Terra (medium) | 30.5 | $0.19 | no |
| Claude Sonnet 5 (medium) | 28.5 | $1 | no |
| GPT-5.6 Luna (medium) | 25.5 | $0.013 | yes |

What follows from it:

- **Astra at medium already beats sol at max** by about three index points at well under its cost, and astra at max matches Fable 5.1 at max. Once live, `gpt-astra-medium` is the cheapest route above sol and the natural consequential challenger; sol at high or xhigh becomes the fallback, not the first choice.
- **Flash is the DeepSeek default.** V4.1 Flash at max ties sol at medium on the index at roughly half the cost, and sits above luna at max. V4 Pro is below Flash and costs over twice as much, so route to it only for a reason the index does not capture.
- **Terra at medium is dominated by luna at max at the same cost.** Prefer `gpt-terra-high` for terra work; if a luna-tier price is the goal, luna's long-context weakness still applies.
- **Sonnet 5 at medium is far off the frontier** on this chart. Its value on the Claude leg is harness fit and the Max subscription, not index per dollar; do not pick it for a metered comparison.
- Every Claude point is above the frontier on cost. That is expected for subscription-billed routes and is not a reason to move Claude proposers off the Claude leg.

## Cross-family verification

A same-family reviewer shares the proposer's blind spots, so Claude work is challenged by a GPT model and GPT work by a Claude model. No model reviews its own output. DeepSeek is the third family: use it as the challenger when the proposer's family and the GPT family have already disagreed, or when the work is metered-cheap enough that Flash is the right price for a second opinion.

| Proposer | Challenger | Escalate to |
|---|---|---|
| `opus-high`, `fable-*` | `gpt-astra-medium` once live, else `gpt-sol-high` | `gpt-astra-high` once live, else `gpt-sol-xhigh` |
| `opus-medium` | `gpt-sol-medium` | `gpt-sol-high` |
| `sonnet-high` | `gpt-terra-high` | `gpt-sol-medium` |
| `sonnet-medium` | `gpt-luna-medium` | `gpt-terra-high` |
| `haiku-summary`, `haiku-basic` | `gpt-luna-low` | `gpt-luna-medium` |
| `gpt-astra-*` | `fable-high` | `fable-xhigh` |
| `gpt-sol-high`, `gpt-sol-xhigh` | `opus-high` | `fable-high` |
| `gpt-sol-medium` | `opus-medium` | `opus-high` |
| `gpt-terra-medium`, `gpt-terra-high` | `sonnet-high` | `opus-medium` |
| `gpt-luna-*` | `sonnet-medium` | `sonnet-high` |
| `deepseek-v4-pro-high`, `deepseek-flash-high` | `opus-high` | `gpt-sol-high` |
| `deepseek-*-medium` | `sonnet-high` | `opus-medium` |
| `deepseek-*-low` | `sonnet-medium` | `sonnet-high` |

Third-family tiebreak: when proposer and challenger disagree and the escalation rung would be the same family as one of them, use `deepseek-flash-high` for Sonnet-tier work and `deepseek-v4-pro-high` for Opus-tier work instead, and report all three positions.

Size the challenger to the cost of being wrong, not to the proposer's rank. Treat a cross-family disagreement as a finding to resolve, not a tie to split: escalate one rung and report both positions.

The review-changes skill picks its single verifier from this table, and that verifier is advised for substantial changes, not required for every change.

With the proxy unavailable there is no cross-family route: fall back to a stronger same-family route and report the verification as same-family. The proxy uses the Codex subscription credential for the GPT leg, so a stale one is fixed with `codex login`, not by rerouting; the DeepSeek leg needs a configured prepaid key and answers `503` without one.

## Slow-path workflow

1. **Discover** only the affected runtime, and only when availability, an alias, or an explicit selection is unresolved:

   ```bash
   python3 scripts/model_selection.py discover --runtime claude --format markdown
   ```

   Codex discovery reads `CODEX_HOME/models_cache.json` and `config.toml`; treat `visibility: list` entries as available and mark hidden ones separately. Claude discovery reads `~/.claude/settings.json`, model fields in `~/.claude.json`, and the CLI help. Claude's `opus`/`sonnet`/`haiku` are aliases, not proof every dated model is enabled, and no supported command enumerates the full entitlement set — preserve that uncertainty. Neither runtime file knows about the gateway: pointed at `utraque`, Claude Code reaches the Codex models too, and `/healthz` is the authority on which are live.

2. **Fetch** the catalog only if discovery does not resolve it. Credentials default to `creds.json` beside this skill; cache to `.cache/llms-models.json`.

   ```bash
   python3 scripts/model_selection.py fetch
   python3 scripts/model_selection.py fetch --refresh
   ```

   Use `ARTIFICIAL_ANALYSIS_API_KEY` or `--credentials PATH` if the key lives elsewhere. Never print, commit, or embed the key. The cache is 24h and falls back to stale data after a failed refresh; pass `--no-stale-if-error` when freshness is required.

3. **Rank** only if still unresolved. Prefer an Artificial Analysis category index when present; otherwise the client uses available benchmark fields from the topic alias list and reports which it used.

   ```bash
   python3 scripts/model_selection.py rank --topic coding --runtime all --format markdown
   python3 scripts/model_selection.py rank --metric livecodebench --format table
   python3 scripts/model_selection.py rank --topic coding --available-only --runtime codex
   python3 scripts/model_selection.py rank --topic general --sort cost-per-intelligence --format markdown
   ```

   `--topic`: general (default), coding, writing, agents, reasoning, math, science, multilingual, multimodal, speed, cost. `--sort`: score (default), cost-per-intelligence, speed, price.

4. **Break down** the benchmarks only to resolve a close or consequential choice:

   ```bash
   python3 scripts/model_selection.py rank --topic coding --metrics all --format json > /tmp/models-coding.json
   python3 scripts/model_selection.py rank --topic coding --metrics livecodebench,scicode --format markdown
   ```

   Load the relevant topic reference before interpreting a score — they are split by capability: [coding](references/benchmarks-coding.md), [writing and knowledge work](references/benchmarks-writing-knowledge.md), [math and science](references/benchmarks-math-science.md), [agents and cross-cutting caveats](references/benchmarks-agents-reasoning.md). [Artificial Analysis API](references/artificial-analysis-api.md) covers field semantics and caching.

5. **Report a shortlist**, not one universal winner: availability, one task-relevant score with its source field, and price; add speed only when latency matters. Report only decision-relevant fields. Call out missing metrics, standalone versus index benchmarks, confidence intervals, and whether a score is model-only or harness-dependent.

## Cost per intelligence

Artificial Analysis prices and `cost_per_task` are API-comparison inputs, not Claude Max quota weights or a weekly allowance. Use observed account meters and task telemetry for account usage; say unknown when unpublished.

`cost_per_intelligence_point = blended_price_per_1m_tokens / selected_score` (score on 0-100); also show `cost_per_100_intelligence_points`, which reads more easily. This normalizes for comparison under one rough token mix — it is not the price of a real task, which depends on prompt and output length, reasoning tokens, cache hits, endpoint, tool calls, and retries.

`price_1m_blended_3_to_1` is used as reported; absent it, the helper falls back to `(input_price + 3 * output_price) / 4`. Do not compare this ratio against a score from a different evaluation family without labeling the denominator.

## Selection rules

- Match the benchmark to the work. A coding index is a first sort, but terminal execution, repo repair, scientific Python, and completion are different skills.
- Treat composite indices as summaries, not ground truth; keep per-benchmark rows and prefer a task-specific benchmark where one exists.
- Writing quality is not a scalar. GDPval and Briefcase cover deliverables and knowledge work; IFBench measures instruction compliance; none capture voice, originality, factual editing, or audience fit.
- Prefer fresh or decontaminated evaluations when models are close — static scores inflate through training overlap, prompt sensitivity, grader choice, and harness differences.
- Do not mix raw percentages, Elo, and index values as if they meant the same thing. The formatter normalizes 0-1 pass rates for display but keeps raw values in JSON.
- Choose a challenger by family first, rank second; a same-family review is a weaker signal at the same price.
- With no local runtime match, distinguish “best in the catalog” from “invokable here.”
- Cite Artificial Analysis when sharing free-API data; the documentation requires attribution.

## Python API

The script is importable. Keep network access and caching in the helper rather than duplicating requests:

```python
from pathlib import Path
from scripts.model_selection import enrich_models, fetch_models, payload_data

payload, cache_info = fetch_models(cache_dir=Path(".cache"))
rows = enrich_models(payload_data(payload), topic="coding")
for row in rows[:10]:
    print(row["name"], row["selected_score"], row["cost_per_100_intelligence_points"])
```

Use `clean_for_json`, `markdown`, or `table` for downstream formatting. Keep the raw `evaluations` and `pricing` objects in exported data so future topic references apply without a new API call.

## Resources

- [Artificial Analysis API](references/artificial-analysis-api.md): local Markdown transcription of the free endpoint contract, fields, errors, attribution, and cache rules.
- [Coding benchmarks](references/benchmarks-coding.md): Terminal-Bench, SciCode, LiveCodeBench, SWE-bench, and coding-index interpretation.
- [Writing and knowledge work](references/benchmarks-writing-knowledge.md): GDPval, AA-Briefcase, AA-LCR, AA-Omniscience, IFBench, and MMLU-Pro.
- [Math and science](references/benchmarks-math-science.md): HLE, GPQA Diamond, CritPt, MATH-500, AIME, and science/coding crossover.
- [Agents and reasoning](references/benchmarks-agents-reasoning.md): tau-style tool use, composite-index weighting, grader and contamination risks, and practical decision heuristics.
