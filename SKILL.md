---
name: model-selection
description: Compare language models on Artificial Analysis benchmarks, price, speed, and task fit, and hold the facts behind the CLAUDE.md routes (proxy, effort mechanics, context limits, evidence). Use for explicit comparisons, uncertain model or effort choices, alias or availability questions, work outside the CLAUDE.md routing and pairing tables, security routing, or periodic calibration. Not for routine spawns or verifier choices those tables already cover. An explicit user choice wins unless unavailable.
---

# Model Selection

A bundled Python client discovers local runtime options, fetches the Artificial Analysis LLM catalog with disk caching, ranks models by task-relevant benchmarks, and formats the evidence.

## Fast path first

For a routine spawn or verifier choice covered by the routing and cross-family pairing tables in `~/.claude/CLAUDE.md`, select that route and stop — no discovery, fetch, or ranking. Take the slow path only for the triggers in the description. An explicit user selection wins, subject to availability.

## Local gateway routes

The `gpt-*` routes reach OpenAI models over the `utraque` proxy on `127.0.0.1:8317`, billed to the Codex subscription. The `deepseek-*` routes reach DeepSeek's Anthropic-compatible endpoint over the same proxy and spend a prepaid DeepSeek API balance, so they are the only metered routes. Route agents live in `~/.claude/agents/`; this skill's `agents/` directory is a Codex interface manifest, not a route directory — do not define routes here.

| Route | Model name sent | Peer Claude route | Route effort |
|---|---|---|---|
| `gpt-astra-medium`, `gpt-astra-high`, `gpt-astra-xhigh` | `astra-medium`, `astra-high`, `astra-xhigh` (GPT-6 Astra) | `opus-high`, `opus-xhigh` | `medium`, `high`, `xhigh` |
| `gpt-sol-high`, `gpt-sol-xhigh` | `sol-high`, `sol-xhigh` (GPT-6.1 Sol) | `sonnet-high` | `high`, `xhigh` |
| `gpt-sol-medium` | `sol-medium` (GPT-6.1 Sol) | `sonnet-high` | `medium` |
| `gpt-luna-low`, `gpt-luna-medium` | `luna-low`, `luna-medium` (GPT-6 Luna) | `haiku-low` | `low`, `medium` |
| `deepseek-flash-low`, `-medium`, `-high` | `deepseek-flash` (V4.1 Flash) plus frontmatter effort | `haiku-*`, `sonnet-medium`, `sonnet-high` | `low`, `medium`, `high` |
| `deepseek-v4-pro-low`, `-medium`, `-high` | `deepseek-v4-pro` (V4 Pro 0813) plus frontmatter effort; no image input | `sonnet-medium`, `opus-medium`, `opus-high` | `low`, `medium`, `high` |

Facts that constrain these routes:

- **Context is 272k tokens on the Codex leg**, whatever the API docs advertise. Never plan a larger task onto a `gpt-*` route. DeepSeek windows are unverified.
- **Keep luna off long context.** Its long-context recall is poor, so it degrades quietly rather than failing.
- **On the Codex leg a suffixed model name is the only way to set effort.** Frontmatter `effort` never reaches that leg; it is bookkeeping for the CLAUDE.md pin rule. A bare alias silently drops to the proxy default (`low` for sol), so never "tidy" agent files back to bare aliases. Confirm with the proxy's per-request log line (`client_model`, `upstream_model`, `effort`).
- **On the DeepSeek leg the model name must be exact** (`deepseek-flash`, `deepseek-v4-pro`; a suffix is rejected) and effort travels in the frontmatter key. The proxy forwards it unvalidated, so a value DeepSeek does not honor fails or degrades upstream.
- **No `ultra` route.** `ultra` is not a valid frontmatter effort; reach it, if ever, by naming `sol-ultra` directly (unverified for GPT-6.1 Sol).
- **Bare aliases float to the newest model with that codename**; pinned names (`sol-6`) keep older ones. The backend withholds new models from older Codex CLI clients, so check `/v1/models` before assuming which model a route runs.
- Do not route to `gpt-5.3-codex-spark` or `codex-auto-review`.

These routes work only when `ANTHROPIC_BASE_URL` names the proxy. The `claude` alias (`claude-smart.sh`) sets it at launch when the proxy answers healthy, so check the environment variable, not `settings.json`. Without it the model name reaches `api.anthropic.com` and is rejected. See `~/.claude/UTRAQUE-SETTINGS-DELTA.md`.

For availability prefer the proxy's own state: `GET /healthz` reports Codex auth, catalog state and model count, transport, and quota, and `GET /v1/models` lists what is routable now (DeepSeek rows only when a DeepSeek key is configured). When the proxy is down every `gpt-*` and `deepseek-*` route fails immediately; Claude routes are unaffected only in sessions launched without the proxy. In a session already routed through it, all requests fail while the proxy is down. The GPT leg uses the Codex subscription credential, so fix a stale one with `codex login`, not by rerouting. The DeepSeek leg answers `503` when no prepaid key is configured.

### Intelligence-cost snapshot

Artificial Analysis Intelligence Index @ cost per index task, as of 2026-10-07. `~` marks a chart reading; `—` is unpublished. AA's effort names are its own settings. Cost is metered only on the DeepSeek leg; on the subscription legs read it as quota burn.

| Model | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| Claude Opus 5.5 | 42 @ $0.55 | 51 @ $1.34 | 54 @ $1.82 | 56 @ $3.46 | 58 @ $5.98 |
| Claude Sonnet 5.5 | 36 @ $0.41 | 41 @ $0.59 | 47 @ $1.08 | 52 @ $2.74 | 56 @ $7.62 |
| Claude Haiku 5.5 | 29 | 34 | 38 | 41 @ $0.12 | 43 @ $0.21 |
| Claude Fable 5.1 | 47 | 49 @ ~$3.2 | 51 | 53 | 53 @ $7.63 |
| GPT-6.1 Sol | 42 @ $0.13 | 48 @ $0.21 | 50 @ $0.32 | 51 @ $0.39 | 52 @ $0.72 |
| GPT-6 Astra | ~46 @ ~$0.8 | ~49.5 @ ~$1.55 | ~51 @ ~$1.75 | ~52.5 @ ~$2.35 | ~53 @ ~$3.3 |
| GPT-6 Luna | ~21 @ ~$0.006 | ~29.5 @ ~$0.018 | ~32 @ ~$0.029 | ~34 @ ~$0.043 | ~37.5 @ ~$0.068 |
| DeepSeek V4.1 Flash | — | — | — | — | ~39.5 @ ~$0.28 |
| DeepSeek V4 Pro 0813 | — | — | — | — | ~36 @ ~$0.68 |

- **Haiku prices by per-request prompt length:** up to 100k tokens $0.10/$0.50 per 1M input/output; above 100k every category rises 5x. That drives the CLAUDE.md rule sending prompts expected to stay under 100k to the haiku routes.
- **Haiku's long-context recall is unmeasured**, so prompts above 100k stay on `sonnet-medium` until it is measured.
- **AA's Sonnet costs predate the 2026-10-07 cache-read cut** ($0.20 to $0.10 per 1M), so they overstate Sonnet's cost until AA re-measures.
- **No `sonnet-xhigh` or `sonnet-max` route:** `opus-high` dominates Sonnet xhigh, and Opus xhigh ties Sonnet max at under half the cost.
- **No `opus-max` route:** Opus xhigh beats max on Terminal-Bench at about 1.7x lower cost.

## Cross-family verification

The pairing table, tiebreak, and proxy-down fallback live in `~/.claude/CLAUDE.md`. In addition:

- If `gpt-sol-high` fails as the challenger for `sonnet-high` or `opus-medium`, use `gpt-astra-medium`, escalating to `gpt-astra-high`.
- `sonnet-high` is also an acceptable routine challenger for `gpt-sol-medium`.
- DeepSeek Flash is a fit challenger when metered-cheap is the right price for a second opinion.

### Security routing

Security work — doing it and reviewing it — goes to `gpt-astra-*`, not a Claude route. Anthropic re-routes most cybersecurity tasks on Opus and Fable to an older Opus, and higher-risk ones on Sonnet visibly fall back to an older Sonnet, so no Claude route is full-strength for security and a Claude route reviewing GPT's security work may be running the older model. Routine bug finding and fixing in normal development is unaffected. Haiku has no fallback: a cyber-classifier decline returns `stop_reason: "refusal"` and stays declined, so `haiku-*` routes never run security work.

With the proxy down, fall back to `opus-high` (or `opus-xhigh`), not Fable, and report both that the check is same-family and that it may be running an older Opus.

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
   python3 scripts/model_selection.py rank --metric artificial_analysis_coding_index --format table
   python3 scripts/model_selection.py rank --topic coding --available-only --runtime codex
   python3 scripts/model_selection.py rank --topic general --sort cost-per-intelligence --format markdown
   ```

   `--topic`: general (default), coding, writing, agents, reasoning, math, science, multilingual, multimodal, speed, cost. `--sort`: score (default), cost-per-intelligence, speed, price.

4. **Break down** the benchmarks only to resolve a close or consequential choice:

   ```bash
   python3 scripts/model_selection.py rank --topic coding --metrics all --format json > /tmp/models-coding.json
   python3 scripts/model_selection.py rank --topic coding --metrics artificial_analysis_coding_index,artificial_analysis_agentic_index --format markdown
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
- With no local runtime match, distinguish "best in the catalog" from "invokable here."
- Cite Artificial Analysis when sharing free-API data; the documentation requires attribution.
