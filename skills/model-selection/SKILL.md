---
name: model-selection
description: Compare language models on Artificial Analysis benchmarks, price, speed, and task fit, and hold the facts behind the CLAUDE.md routes (proxy, effort mechanics, context limits, evidence). Use for explicit comparisons, uncertain model or effort choices, alias or availability questions, work outside the CLAUDE.md routing and pairing tables, security routing, or periodic calibration. Not for routine spawns or verifier choices those tables already cover. An explicit user choice wins unless unavailable.
---

# Model Selection

A bundled Python client discovers local runtime options, fetches the Artificial Analysis LLM catalog with disk caching, ranks models by task-relevant benchmarks, and formats the evidence. Paths below are relative to this skill's directory (`${CLAUDE_SKILL_DIR}`).

## Fast path first

For a routine spawn or verifier choice covered by the routing and cross-family pairing tables in CLAUDE.md (the global instructions from the `craig-core` plugin), select that route and stop — no discovery, fetch, or ranking. Take the slow path only for the triggers in the description. An explicit user selection wins, subject to availability.

## Local gateway routes

The `gpt-*` routes reach OpenAI models over the `utraque` proxy on `127.0.0.1:8317`, billed to the Codex subscription. The `deepseek-*` routes reach DeepSeek's Anthropic-compatible endpoint over the same proxy and spend a prepaid DeepSeek API balance, so they are the only metered routes. There is one route agent per model, and every `Agent` call passes `effort` (written "`route` @ `effort`", e.g. `craig-core:opus` @ `high`). The Claude route agents (`craig-core:opus`, `craig-core:sonnet`, `craig-core:haiku`, `craig-core:fable`) ship in the `craig-core` plugin; the `gpt-*` and `deepseek-*` route agents live in `~/.claude/agents/` on Craig's Mac only. When these routes count as available, and the Claude-only fallback when they do not, is the Route availability rule in CLAUDE.md. This skill's `agents/` directory is a Codex interface manifest, not a route directory — do not define routes here.

| Route | Model name sent | Peer Claude route | Allowed efforts |
|---|---|---|---|
| `gpt-astra` | `astra` (GPT-6 Astra) | `craig-core:opus` @ `high`, `craig-core:opus` @ `xhigh` | `medium`, `high`, `xhigh` |
| `gpt-sol` | `sol` (GPT-6.1 Sol) | `craig-core:sonnet` @ `high` | `medium`, `high`, `xhigh` |
| `gpt-luna` | `luna` (GPT-6 Luna) | `craig-core:haiku` @ `low` | `low`, `medium` |
| `gpt-terra` | `terra` (GPT-6.1 Terra) | `craig-core:haiku` @ `xhigh` (at `medium`), `craig-core:haiku` @ `max` (at `high`) | `medium`, `high` |
| `deepseek-flash` | `deepseek-flash` (V4.1 Flash) | `craig-core:haiku` (at `low`), `craig-core:sonnet` @ `medium` (at `medium`), `craig-core:sonnet` @ `high` (at `high`) | `low`, `medium`, `high` |
| `deepseek-v4-pro` | `deepseek-v4-pro` (V4 Pro 0813); no image input | `craig-core:sonnet` @ `medium` (at `low`), `craig-core:opus` @ `medium` (at `medium`), `craig-core:opus` @ `high` (at `high`) | `low`, `medium`, `high` |

Effort mechanics (measured on Claude Code 2.1.306, 2026-10-21):

- **The Agent tool's `effort` parameter** (`low|medium|high|xhigh|max`) reaches the API as `output_config.effort`. Precedence: Agent `effort` > agent frontmatter `effort` > parent session effort. A forgotten parameter silently inherits the parent's effort, which is why CLAUDE.md requires it; a `craig-core` PreToolUse hook enforces it.
- **The Agent `model` parameter accepts only `sonnet|opus|haiku|fable`.** Any other string, including a GPT alias or a full Claude model ID, fails with `InputValidationError`. A non-Claude model therefore needs an agent file whose frontmatter `model:` names it, which is why the `gpt-*` and `deepseek-*` routes are agent files.
- **`utraque` resolves effort as model-name suffix > body `output_config.effort` > default**, and logs `effort_source` (`suffix|body|default`) beside `effort_requested` and `effort_applied`. Use bare aliases (`sol`, `astra`, `luna`, `terra`) so the Agent parameter decides; a suffixed alias (`sol-high`) would override it.
- **The Codex leg clamps effort to the model's live catalog levels**, and sends it unclamped when the catalog is unavailable. Check `effort_applied` in the log line, not the request.
- **The DeepSeek leg maps** `low`→`low`, `medium`→`high`, `high`→`high`, `xhigh`→`high`, `max`→`max`, because DeepSeek accepts only `low`, `high`, and `max` ([thinking mode](https://api-docs.deepseek.com/guides/thinking_mode)). So `medium` and `high` run identically there, and `xhigh` buys nothing. DeepSeek model names take no suffix.
- **`utraque` translates Claude Code's mid-conversation `tool_addition` and `tool_removal` blocks** for both the GPT and DeepSeek legs: it hoists added tools into the tools list and honors removals.

Facts that constrain these routes:

- **Context is 272k tokens on the Codex leg**, whatever the API docs advertise. Never plan a larger task onto a `gpt-*` route. DeepSeek windows are unverified.
- **Keep luna off long context.** Its long-context recall is poor, so it degrades quietly rather than failing.
- **`gpt-terra` is provisional.** AA has published no coding or agentic sub-index and no long-context recall for it, and AA lists a 1M context although the Codex leg caps at 272k. Keep prompts under 100k tokens until recall is measured, and check quota burn and `effort_applied` in the proxy log before promoting it.
- **Route agent files carry the bare model name and no `effort` key.** The Agent `effort` parameter is the only effort setting; confirm what a request ran with from the proxy's per-request log line (`client_model`, `upstream_model`, `effort_source`, `effort_requested`, `effort_applied`).
- **On the DeepSeek leg the model name must be exact** (`deepseek-flash`, `deepseek-v4-pro`; a suffix is rejected).
- **No `ultra` route.** The Agent `effort` enum stops at `max`. Reaching `ultra`, if ever, needs a dedicated agent file whose `model:` is the suffixed name `sol-ultra` (unverified for GPT-6.1 Sol).
- **Bare aliases float to the newest model with that codename**; pinned names (`sol-6`) keep older ones. The backend withholds new models from older Codex CLI clients, so check `/v1/models` before assuming which model a route runs.
- Do not route to `gpt-5.3-codex-spark` or `codex-auto-review`.

These routes work only when `ANTHROPIC_BASE_URL` is `http://127.0.0.1:8317`. The `claude` alias (`claude-smart.sh`) sets it at launch when the proxy answers healthy, so check the environment variable, not `settings.json`. Without it the model name reaches `api.anthropic.com` and is rejected. See `~/.claude/UTRAQUE-SETTINGS-DELTA.md`.

For availability prefer the proxy's own state: `GET /healthz` reports Codex auth, catalog state and model count, transport, and quota, and `GET /v1/models` lists what is routable now (DeepSeek rows only when a DeepSeek key is configured). When the proxy is down every `gpt-*` and `deepseek-*` route fails immediately; Claude routes are unaffected only in sessions launched without the proxy. In a session already routed through it, all requests fail while the proxy is down. The GPT leg uses the Codex subscription credential, so fix a stale one with `codex login`, not by rerouting. The DeepSeek leg answers `503` when no prepaid key is configured.

### Intelligence-cost snapshot

Artificial Analysis Intelligence Index @ cost per index task, as of 2026-10-26. `~` marks a chart reading; `—` is unpublished. AA's effort names are its own settings. Cost is metered only on the DeepSeek leg; on the subscription legs read it as quota burn.

| Model | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| Claude Opus 5.5 | 42 @ $0.55 | 51 @ $1.34 | 54 @ $1.82 | 56 @ $3.46 | 58 @ $5.98 |
| Claude Sonnet 5.5 | 36 @ $0.35 | 41 @ $0.48 | 47 @ $0.88 | 52 @ $2.01 | 56 @ $5.46 |
| Claude Haiku 5.5 | 30 @ $0.025 | 35 @ $0.047 | 38 @ $0.079 | 41 @ $0.12 | 43 @ $0.21 |
| Claude Fable 5.1 | 47 @ $2.37 | 49 @ $2.98 | 51 @ $3.91 | 53 @ $5.98 | 53 @ $7.63 |
| GPT-6.1 Sol | 42 @ $0.13 | 48 @ $0.21 | 50 @ $0.32 | 51 @ $0.39 | 52 @ $0.72 |
| GPT-6 Astra | 46 @ $0.82 | 50 @ $1.54 | 51 @ $1.73 | 52 @ $2.31 | 53 @ $3.26 |
| GPT-6.1 Terra | 36 @ $0.055 | 41 @ $0.095 | 44 @ $0.13 | 45 @ $0.19 | 48 @ $0.40 |
| GPT-6 Luna | 22 @ $0.0045 | 30 @ $0.018 | 33 @ $0.029 | 35 @ $0.042 | 38 @ $0.068 |
| DeepSeek V4.1 Flash | — | — | — | — | ~39.5 @ ~$0.28 |
| DeepSeek V4 Pro 0813 | — | — | — | — | ~36 @ ~$0.68 |

- **Haiku prices by per-request prompt length:** up to 100k tokens $0.10/$0.50 per 1M input/output; above 100k every category rises 5x. That drives the CLAUDE.md rule sending prompts expected to stay under 100k to `craig-core:haiku`.
- **Haiku's long-context recall is unmeasured**, so prompts above 100k stay on `craig-core:sonnet` @ `medium` until it is measured.
- **No `craig-core:sonnet` @ `xhigh` or @ `max`:** `craig-core:opus` @ `high` dominates Sonnet xhigh, and `craig-core:opus` @ `xhigh` ties Sonnet max at about 63% of the cost.
- **No `craig-core:opus` @ `max`:** Opus xhigh beats max on Terminal-Bench at about 1.7x lower cost.

## Cross-family verification

The pairing table with its Claude-only columns, the tiebreak, and the security override live in CLAUDE.md. In addition, when cross-family routes are available:

- If `gpt-sol` @ `high` fails as the challenger for `craig-core:sonnet` @ `high` or `craig-core:opus` @ `medium`, use `gpt-astra` @ `medium`, escalating to `gpt-astra` @ `high`.
- `craig-core:sonnet` @ `high` is also an acceptable routine challenger for `gpt-sol` @ `medium`.
- `deepseek-flash` is a fit challenger when metered-cheap is the right price for a second opinion.

### Security routing

Why CLAUDE.md sends security work — doing it and reviewing it — to `gpt-astra` and, Claude-only, to `craig-core:opus` @ `high` or @ `xhigh` but never `craig-core:fable` or `craig-core:haiku`: Anthropic re-routes most cybersecurity tasks on Opus and Fable to an older Opus, and higher-risk ones on Sonnet visibly fall back to an older Sonnet, so no Claude route is full-strength for security and a Claude route reviewing GPT's security work may be running the older model. Routine bug finding and fixing in normal development is unaffected. Haiku has no fallback: a cyber-classifier decline returns `stop_reason: "refusal"` and stays declined, so `craig-core:haiku` never runs security work. A Claude-only security check is reported as same-family and as possibly run on an older Opus.

## Slow-path workflow

1. **Discover** only the affected runtime, and only when availability, an alias, or an explicit selection is unresolved:

   ```bash
   python3 scripts/model_selection.py discover --runtime claude --format markdown
   ```

   Codex discovery reads `CODEX_HOME/models_cache.json` and `config.toml`; treat `visibility: list` entries as available and mark hidden ones separately. Claude discovery reads `~/.claude/settings.json`, model fields in `~/.claude.json`, and the CLI help. Claude's `opus`/`sonnet`/`haiku` are aliases, not proof every dated model is enabled, and no supported command enumerates the full entitlement set — preserve that uncertainty. Neither runtime file knows about the gateway: pointed at `utraque`, Claude Code reaches the Codex models too, and `/healthz` is the authority on which are live.

2. **Fetch** the catalog only if discovery does not resolve it. The key comes from `ARTIFICIAL_ANALYSIS_API_KEY`; if that is unset and the 1Password CLI `op` is on PATH, from `op read "$ARTIFICIAL_ANALYSIS_OP_REF"` (default `op://Private/Artificial Analysis/credential`). The catalog caches to `llms-models.json` in `$MODEL_SELECTION_CACHE_DIR`, default `~/.cache/model-selection/`.

   ```bash
   python3 scripts/model_selection.py fetch
   python3 scripts/model_selection.py fetch --refresh
   ```

   Never print, commit, or embed the key, and never write it to a file beside the skill. The cache is 24h and falls back to stale data after a failed refresh; pass `--no-stale-if-error` when freshness is required.

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
