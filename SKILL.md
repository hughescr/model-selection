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
| `gpt-astra-medium`, `gpt-astra-high`, `gpt-astra-xhigh` | `astra-medium`, `astra-high`, `astra-xhigh` (`gpt-6-astra`) | Consequential challenge above sol (`opus-high` and up, design calls, security); the hardest or tenacity-needing problems; work sol stalled on. `astra-medium` is the escalation for `opus-medium` (and for when sol stalls); `astra-high` the escalation for `sonnet-high`. | `opus-high`, `opus-xhigh` (`astra-medium` also escalates `opus-medium`) | `medium`, `high`, `xhigh` | `medium` | `low`-`ultra` | Mixed: astra max (~53 @ ~$3.3, 2026-09-28 chart) sits below its Claude peer `opus-high` (54 @ $1.82, AA page 2026-10-01) — no Astra effort reaches `opus-high`, and `opus-medium` (51 @ $1.34) beats astra medium/high (~49.5 @ ~$1.55, ~51 @ ~$1.75). Astra low ~46 @ ~$0.8 is inferred (dot obscured on the chart). Route verified live 2026-09-11; catalog says 272k context. GPT-6.1 Sol (AA-measured 2026-10-01: high 50 @ $0.32, max 52 @ $0.72) beats astra medium (~49.5) at about a fifth of its cost, so `gpt-sol-high` is the routine challenger for `sonnet-high` and `opus-medium` and astra is the escalation rung. AA lists GPT-6 Astra at 53 (max). |
| `gpt-sol-high`, `gpt-sol-xhigh` | `sol-high`, `sol-xhigh` (`gpt-6.1-sol`: the bare alias floats to it; `sol-6` pins `gpt-6-sol`) | Co-default implementation route with `sonnet-high` (multi-file GPT leaf changes at `high`); heavy work, complex debugging, long-horizon agent runs. Also the routine cross-family challenger (`high`) for `sonnet-high` and `opus-medium` (`xhigh` is not a challenger but is a cheap +1 when it matters). Consequential review of `opus-high` and above stays on astra. | `sonnet-high` (capability: GPT-6.1 Sol measured high 50, xhigh 51 vs 47); also challenges `opus-medium` (~1 below it); role peer of `opus-high` (~4 below) | `high`, `xhigh` | `low` (not rechecked for GPT-6.1) | OpenAI lists `low`-`max` for GPT-6.1 Sol (`ultra` unverified; see below) | Measured by AA 2026-10-01 (GPT-6.1 Sol, which the route runs): high 50 @ $0.32 (60 t/s), xhigh 51 @ $0.39 (55 t/s), max 52 @ $0.72 (64 t/s): above `sonnet-high` (47) and astra medium (~49.5), ~1 below `opus-medium` (~51), ~4 below `opus-high` (54). xhigh is +1 over high for ~22% more cost: still prefer `sol-high` for routine work. |
| `gpt-sol-medium` | `sol-medium` (`gpt-6.1-sol`: the bare alias floats to it; `sol-6` pins `gpt-6-sol`) | Normal substantive leaf work: co-default implementation route with `sonnet-high` (the default GPT leaf). Also routine verification, or a second opinion on another agent's work. | `sonnet-high` (capability, measured 48 vs 47 at about a fifth of the AA cost); ~3 below `opus-medium` | `medium` | `low` (not rechecked for GPT-6.1) | OpenAI lists `low`-`max` for GPT-6.1 Sol (`ultra` unverified; see below) | Measured by AA 2026-10-01 (GPT-6.1 Sol, which the route runs): medium 48 @ $0.21 (54 t/s): level with `sonnet-high` (47 @ $1.08) at about a fifth of the AA cost, ~3 below `opus-medium` (~51). GPT-6.1 Sol low (42 @ $0.13, 60 t/s) is about `sonnet-medium` (41); no `gpt-sol-low` route exists and none is planned. |
| `gpt-luna-medium` | `luna-medium` (`gpt-6-luna`: proxy lists it as of 2026-09-28) | Bounded work with objective checks: extraction, classification, mechanical refactors. Short inputs only. | `haiku-low` | `medium` | `medium` | `low`-`max` | Weak: luna medium (~29.5) is level with Haiku 5.5 low (29), and luna max (~37.5) is below Haiku xhigh (41) and `sonnet-medium` (41). Its case is cost and family only, not capability. |
| `gpt-luna-low` | `luna-low` (`gpt-6-luna`: proxy lists it as of 2026-09-28) | Cheap mechanical work and summaries. | `haiku-low` | `low` | `medium` | `low`-`max` | Weak: luna low (~21 @ ~$0.006) is below Haiku 5.5 low (29) and well below `haiku-xhigh` (41); luna max (~37.5) is still below it. A cost and family peer, not a capability peer. |
| `deepseek-flash-low`, `deepseek-flash-medium`, `deepseek-flash-high` | `deepseek-flash` (DeepSeek V4.1 Flash) plus frontmatter effort | The default DeepSeek route and the cheapest third-family challenger; peers the Haiku routes, `sonnet-medium`, and `sonnet-high` by tier. | `haiku-*`, `sonnet-medium`, `sonnet-high` | `low`, `medium`, `high` | DeepSeek's own default | forwarded unvalidated; `low`-`high` exercised | Index position is strong; the per-tier peering is inferred from the single max-effort point AA publishes. Flash max (39.5) is below `sonnet-medium` (41) and well below `sonnet-high` (47), so the flash tier peering with Sonnet is a cost match, not a capability match. Haiku 5.5 xhigh (41 @ $0.12) also beats flash max on score at under half the AA cost, so against the Haiku routes flash is a cost-and-family peer only. |
| `deepseek-v4-pro-low`, `deepseek-v4-pro-medium`, `deepseek-v4-pro-high` | `deepseek-v4-pro` (DeepSeek V4 Pro 0813) plus frontmatter effort | Only when a task needs something the index does not measure; on the index Flash dominates it. No image input. | `sonnet-medium`, `opus-medium`, `opus-high` | `low`, `medium`, `high` | DeepSeek's own default | forwarded unvalidated; `low`-`high` exercised | The peering is a role placeholder, not evidence: AA puts Pro below Flash at over twice the cost. |

Facts that constrain these routes:

- **Context is 272k tokens on the Codex leg, not the 1M the API docs advertise.** Never plan a larger task onto a `gpt-*` route; the catalog gives astra the same 272k. GPT-6.1 Sol's API docs say 1.05M (922k max input); AA also lists 1M (2026-10-01), but its Codex-leg window is still unverified, so keep assuming 272k. DeepSeek windows are unverified.
- **Keep luna off long context.** Its long-context recall is 41.3% against sol's 91.5%, so it degrades quietly rather than failing.
- **On the Codex leg a suffixed model name is the only way to set effort.** Frontmatter `effort` never reaches that leg: utraque's `chooseEffort` reads a model-name suffix, then two `Options` fields no non-test code assigns, then the catalog default. So agent files send `sol-high`, `luna-low`, and the frontmatter `effort` key is bookkeeping for the CLAUDE.md pin rule. A bare alias silently drops to the proxy default — `low` for sol, the worst case on a consequential-review route.
- **On the DeepSeek leg the model name must be exact** (`deepseek-flash`, `deepseek-v4-pro`; a suffix like `deepseek-flash-high` is rejected as unrecognised) and effort travels in the frontmatter key instead. The proxy forwards the effort field as-is, so a value DeepSeek does not honor fails or degrades upstream rather than at the proxy.
- **`ultra` is not a valid frontmatter effort.** Reach it only via a suffixed name (`sol-ultra`), at roughly triple the cost for one to three points. OpenAI's GPT-6.1 Sol docs list `low`-`max` with no `ultra`, so `sol-ultra` may fail or be clamped; unverified.
- The proxy accepts a bare alias (`sol`), a pinned name (`sol-5.6`, `sol-6`, `sol-6.1`), a raw slug (`gpt-5.6-sol`), or an effort suffix (`sol-high`); the model picker shows these as `anthropic-compat.<alias>`. Whether a pinned name takes an effort suffix (`sol-6-high`) is unverified.
- Do not route to `gpt-5.3-codex-spark` (excluded by choice) or `codex-auto-review` (hidden and undocumented).
- **GPT-6 Luna** (`gpt-6-luna`): API price per 1M tokens, input/output, $0.10/$0.50. Context window and effort list are not published. The luna long-context warning above (41.3% recall) was measured on GPT-5.6 Luna; treat it as unverified for GPT-6 Luna and keep it in force until measured.
- **GPT-6.1 Sol** (`gpt-6.1-sol`; Codex and ChatGPT Work for Plus/Pro/Business/Enterprise/Edu, not yet ChatGPT Chat; API Responses, Chat Completions, Batch). $2/$10 per 1M input/output; cached input $0.10. API docs: 1.05M context (922k max input), 128k max output, efforts `low` / `medium` (default) / `high` / `xhigh` / `max`, knowledge cutoff 2026-04-30. An "Ultrafast" mode (up to 8x token speed in Codex) is promised "in the coming days". No GPT-6.1 Luna or Astra. AA measured it 2026-10-01 (low 42, medium 48, high 50, xhigh 51, max 52; see the GPT-6.1 Sol measurement below).
- **utraque's bare aliases float to the newest version carrying a codename** (`internal/router/registry.go`), so `gpt-sol-*` routes run GPT-6.1 Sol and `gpt-luna-*` routes run GPT-6 Luna with no agent-file change; pinned names (`sol-6`, `sol-5.6`, `luna-5.6`) keep older models. utraque reads the Codex CLI version only at startup and sends it as `client_version` on catalog fetches, and the backend withholds new models from older clients, so check `/v1/models` before assuming which model a route runs. Serving and the proxy's default effort for GPT-6.1 Sol are not verified.

These routes work only when `ANTHROPIC_BASE_URL` names the proxy. The `claude` alias (`claude-smart.sh`) sets it at launch when the proxy answers healthy, so check the environment variable, not `settings.json`. Without it the model name reaches `api.anthropic.com` and is rejected. See `~/.claude/UTRAQUE-SETTINGS-DELTA.md`.

For availability prefer the proxy's own state: `GET /healthz` reports Codex auth, catalog state and model count, transport, and quota, and `GET /v1/models` lists what is routable now. The live catalog is the authority on which models and efforts exist; DeepSeek rows appear only when a DeepSeek key is configured. When the proxy is down every `gpt-*` and `deepseek-*` route fails immediately; Claude routes are unaffected.

### Intelligence-cost snapshot

Artificial Analysis Intelligence Index against cost per index task, from the 2026-09-28 AA chart ("Intelligence Index vs. Cost per Intelligence Index Task") and AA model pages. Readings marked ~ are approximate chart readings; unmarked figures are exact AA page values. AA's effort names are its own settings, not route tiers. Cost is metered only on the DeepSeek leg; for the two subscription legs treat it as a quota-burn proxy. With GPT-6.1 Sol included, Sol xhigh dominates Opus medium at index 51 ($0.39 versus $1.34), and Sol max dominates Sonnet xhigh at index 52 ($0.72 versus $2.74). Opus high, xhigh, and max remain nondominated among the listed points. No Sonnet 5.5 point is on the Pareto line. DeepSeek (2026-09-11 chart): V4.1 Flash max ~39.5 @ ~$0.28, V4 Pro 0813 max ~36 @ ~$0.68. Fable 5.1 with fallback (2026-09-11 chart): max ~53 @ ~$8, medium ~49 @ ~$3.2.

**Opus 5.5.** `claude-opus-5-5` ships with 1M context (AA) and efforts `low` / `medium` (default) / `high` / `xhigh` / `max`; the `opus` alias resolves to it (this session runs on it; not independently verified from a spawned agent). Anthropic says it "performs at the level of Claude Fable 5.1 on most work." AA Intelligence Index v4.3.2 by effort:

| Effort | Opus 5.5 | Fable 5.1 | GPT-6 Astra | Opus 5.5 AA page, index @ cost/task |
|---|---|---|---|---|
| max | 58 | 53 | 53 | 58 @ $5.98 (90 t/s) |
| xhigh | 56 | 53 | 52 | 56 @ $3.46 (78 t/s) |
| high | 54 | 51 | 51 | 54 @ $1.82 (73 t/s) |
| medium | 51 | 49 | 50 | 51 @ $1.34 (72 t/s) |
| low | 42 | 47 | 46 | 42 @ $0.55 (72 t/s) |

Last column: exact AA page values, read 2026-10-01 (https://artificialanalysis.ai/models/releases/claude-opus-5-5). GPT-6.1 Sol low (42 @ $0.13) ties Opus 5.5 low (42 @ $0.55) at about a quarter of the cost.

Fable 5.1 (max) is $7.63 on AA's 2026-09-22 page.

Terminal-Bench 4.0 (Anthropic's chart; GPT figures as OpenAI reported them): Opus 5.5 low 38.5%, medium 57.5%, high 64%, xhigh 66.5%, max 65%.

Most cybersecurity tasks on Opus 5.5 and on Fable are re-routed by Anthropic to Opus 4.8; routine bug finding and fixing in normal development is unaffected — see Security routing below.

**Haiku 5.5.** `claude-haiku-5-5`, released 2026-10-07; 1M context, 128k max output, knowledge cutoff Jun 2026 (https://platform.claude.com/docs/en/models/haiku-5-5/overview). Same tokenizer as Claude 4.7+: ~30% more tokens than Haiku 4.5 for the same text, so 100k Haiku 5.5 tokens is about 77k Haiku 4.5-era tokens. Efforts `low` / `medium` / `high` / `xhigh` / `max`, default `medium` on the API and in Claude Code: the first Haiku-class model with adjustable effort (https://www.anthropic.com/claude-haiku-5-5; platform docs effort page). The Claude Code `haiku` alias resolves to it on the Anthropic API (Haiku 4.5 on Bedrock, Vertex, and Foundry) and needs Claude Code v2.1.293 or later (https://code.claude.com/docs/en/model-config); verified live 2026-10-07 from a spawned agent with `model: haiku`, which reported `claude-haiku-5-5`. So `haiku-low`, `haiku-xhigh`, and `haiku-max` run Haiku 5.5.

Price per 1M tokens is tiered by per-request prompt length (https://platform.claude.com/docs/en/about-claude/pricing). Prompt up to 100,000 tokens: input $0.10, output $0.50, cache write $0.125 (5m) / $0.20 (1h), cache read $0.01. Prompt above 100,000 tokens: $0.50 / $2.50 / $0.625 / $1.00 / $0.05, so every category, output included, rises 5x. Batch is 50% off. Whether cached-read tokens count toward the 100k is unverified. It is the only Claude 4.6+ model without flat 1M pricing. Even above 100k its list input and output price is a quarter of Sonnet 5.5's.

AA Intelligence Index (https://artificialanalysis.ai/models/releases/claude-haiku-5-5, read 2026-10-07), index @ cost per index task: max 43 @ $0.21; xhigh 41 @ $0.12; high 38; medium 34; low 29. Costs for high, medium, and low are not shown, but all are at least $0.12 because AA names xhigh the lowest-cost variant (up to 1.7x cost variation across variants). Output speed is not published. AA lists one price ($0.10/$0.50) with no tiers, so its cost per task likely ignores the above-100k tier (unverified).

- **Haiku xhigh (41 @ $0.12) ties Sonnet 5.5 medium (41 @ $0.59) at about a fifth of the cost.** It beats DeepSeek V4.1 Flash max (~39.5 @ ~$0.28) and GPT-6 Luna max (~37.5 @ ~$0.068) on score. Haiku max (43 @ $0.21) is about GPT-6.1 Sol low (42 @ $0.13), and is +2 over xhigh for ~75% more cost.
- **Haiku low scores 29 and costs no less per task than xhigh on AA**, so its only case is latency, which is unmeasured.
- Anthropic's chart (effort unlabeled): Terminal-Bench 4.0 39.2% (Sonnet 5.5 70.6%, Haiku 4.5 0.0%, GPT-6 Luna 16.4%); FrontierCode 1.1 46.4% (Sonnet 5.5 xhigh 52.1%, Luna 42.4%); OSWorld 2.1 offline 72.4% (Sonnet 83.9%, Luna 48.9%); HLE with tools 57.4% (Sonnet 64.5%); GDPval-AA v2.1 1620 (Sonnet 1840, Luna 1437). Anthropic positions it for summaries, compaction, queries, classification, and sub-agents.
- **Long-context recall is unpublished.** That is why prompts above 100k tokens stay on `sonnet-medium` until it is measured.
- **Security:** Haiku 5.5 has no server-side fallback. A cyber-classifier decline returns `stop_reason: "refusal"` and stays declined, a visible failure rather than a silent downgrade. Its cyber safeguards allow more defensive work than Sonnet 5.5's but still block pentesting and attacker techniques (platform docs refusals-and-fallback; anthropic.com/claude-haiku-5-5).

**GPT-6 Luna and Astra.** Vendor claims: DeepSWE — Luna max 66.6%. AutomationBench — Astra low 30.3%, Astra max 41.4%, Opus 5.5 40.0% (Anthropic's page).

AA-measured (2026-09-28 chart; index @ cost/task; ~ = approximate reading):

| Effort | GPT-6 Luna | GPT-6 Astra |
|---|---|---|
| low | ~21 @ ~$0.006 | ~46 @ ~$0.8 (inferred: dot obscured by a chart label) |
| medium | ~29.5 @ ~$0.018 | ~49.5 @ ~$1.55 |
| high | ~32 @ ~$0.029 | ~51 @ ~$1.75 |
| xhigh | ~34 @ ~$0.043 | ~52.5 @ ~$2.35 |
| max | ~37.5 @ ~$0.068 | ~53 @ ~$3.3 |

**Sonnet 5.5.** `claude-sonnet-5-5` (all platforms) ships with 1M context (AA), API price $2/$10 per 1M input/output (cache read $0.10 since 2026-10-07 per the release notes, 0.05x input, the same ratio as Opus 5.5's $0.20 cache read; cache write $2.50 for 5m, $4.00 for 1h), and efforts `low` / `medium` / `high` / `xhigh` / `max`: default `medium` in Claude Code and apps, `high` on the API. The `sonnet` alias resolves to it (verified from a spawned `sonnet-high` agent on 2026-09-28), so `sonnet-high` and `sonnet-medium` run Sonnet 5.5. AA Intelligence Index, measured 2026-09-28 (with default fallback), and Anthropic's chart readings (approximate; cost is Anthropic's per-attempt, not AA's):

| Sonnet 5.5 effort | AA index @ AA cost/task | Terminal-Bench 4.0 (~, $/attempt) | FrontierCode v1.1 (~, $/task) | CursorBench 4.0 (~, $/task) |
|---|---|---|---|---|
| low | 36 @ $0.41 (no longer on AA's page as of 2026-10-01: "not publicly available"; 88 t/s) | 20% @ $0.75 | 29% @ $0.19 | 36% @ $0.5 |
| medium | 41 @ $0.59 (92 t/s) | 29% @ $0.85 | 36.5% @ $0.24 | 39% @ $0.7 |
| high | 47 @ $1.08 (94 t/s) | 43% @ $1.9 | 49.4% @ $0.43 | 48% @ $1.7 |
| xhigh | 52 @ $2.74 (103 t/s) | 61.5% @ $5.3 | 52.2% @ $1.6 | 53% @ $3.8 |
| max | 56 @ $7.62 (139 t/s) | 70.6% @ $12.7 | 46.2% @ $21 | 55.5% @ $9.7 |

AA page values for Sonnet 5.5 re-read 2026-10-01 (https://artificialanalysis.ai/models/releases/claude-sonnet-5-5); AA has not re-measured since the 2026-10-07 cache-read price cut, so its Sonnet 5.5 cost per task figures use the old cache price. GPT-6.1 Sol high (50 @ $0.32) sits between `sonnet-high` (47) and Sonnet 5.5 xhigh (52 @ $2.74).

Opus 5.5 on the same charts (Anthropic's, approximate; low / medium / high / xhigh / max): Terminal-Bench 38.5% @ $1.3, 57.5% @ $2.9, 64% @ $3.9, 66.5% @ $7.3, 65% @ $11.5. FrontierCode 47.3% @ $0.42, 54.6% @ $0.8, 54% @ $1.1, 51.4% @ $2.2, 54.4% @ $6. CursorBench 43.7% @ $1.2, 52.5% @ $2.9, 56% @ $3.9, 56% @ $7, 57.8% @ $13. Sonnet 5.5 max is the top Terminal-Bench point above every Opus 5.5 effort, but at $12.7. FrontierCode max scores below xhigh because at max Sonnet 5.5 more often ran Claude Code's code-review skill (many sub-agents), causing timeouts or out-of-scope edits (Anthropic footnote). Single-effort Sonnet 5.5 vs Opus 5.5: GDPval-AA v2.1 1844 vs 1846, OSWorld 2.1 80.1% vs 81.8%, HLE with tools 64.5% vs 67.7%.

Security: on Sonnet 5.5, higher-risk cybersecurity tasks visibly fall back to Sonnet 5; routine bug finding and fixing is unaffected — see Security routing below.

What follows from it:

- **Astra is the escalation rung above sol, not the routine challenger.** GPT-6.1 Sol high (50 @ $0.32) beats astra medium (~49.5 @ ~$1.55) at about a fifth of the cost, so `gpt-sol-high` is the routine challenger and astra the escalation — see Cross-family verification. Astra at max matches Fable 5.1 at max.
- **Flash is the DeepSeek default; its case is billing and family, not the index.** GPT-6.1 Sol medium (48 @ $0.21) beats V4.1 Flash max (39.5 @ $0.28) outright, so Flash's case is metered billing and third-family diversity only. V4 Pro is below Flash and costs over twice as much, so route to it only for a reason the index does not capture.
- **Sonnet 5.5 trails Opus 5.5 by about one effort step** on Anthropic's charts (Sonnet high ≈ Opus low, Sonnet xhigh ≈ Opus medium, approximate) at lower cost per step. On AA, medium (41 @ $0.59) beats DeepSeek Flash max (39.5) but only ties Haiku 5.5 xhigh (41 @ $0.12) at about five times the cost. Its value on the Claude leg is still harness fit and the Max subscription.
- **Small tasks go to Haiku 5.5; `sonnet-medium` is for large context.** Prompts expected to stay under 100k Haiku 5.5 tokens route to `haiku-xhigh` by default, `haiku-low` for latency-sensitive mechanical work and summaries, `haiku-max` when a small task needs a bit more. Above 100k tokens Haiku's price rises 5x (still a quarter of Sonnet's list price) and its long-context recall is unmeasured, so bounded work over large context stays on `sonnet-medium` until recall is measured. Price tiers by per-request prompt length, so count the files an agent will read, not only the spawn prompt.
- **No `sonnet-xhigh` or `sonnet-max` route.** Opus 5.5 high dominates Sonnet 5.5 xhigh: AA 54 @ $1.82 vs 52 @ $2.74; Terminal-Bench ~64% vs ~61.5% at lower cost per attempt ($3.9 vs $5.3); CursorBench ~56% vs ~53% at about the same cost ($3.9 vs $3.8). Opus xhigh (56 @ $3.46) ties Sonnet max (56 @ $7.62) at under half the cost. Anthropic-chart readings are approximate. Sonnet max tops Terminal-Bench but at ~$12.7 and scores below xhigh on FrontierCode.
- **Open question: is `sonnet-high` still the right default leaf?** On AA, Opus 5.5 medium (51 @ $1.34) beats Sonnet 5.5 high (47 @ $1.08): +4 points for ~25% more cost. Opus 5.5 low (42 @ $0.55) beats Sonnet 5.5 medium (41 @ $0.59) outright, and no Sonnet 5.5 point is on the Pareto line. Anthropic's own coding charts (FrontierCode, CursorBench) favour Sonnet more than AA does. The 2026-10-07 Sonnet 5.5 cache-read cut ($0.20 to $0.10 per 1M) strengthens `sonnet-high` here: Craig estimates it lowers the effective cost of agentic Sonnet 5.5 work by ~20%, which would widen Opus medium's cost premium over Sonnet high from ~25% to ~55% ($1.34 vs ~$0.86). That is Craig's estimate; Anthropic published no such figure and AA has not re-measured. Opus 5.5's cache read was already 0.05x input, so Opus cost is unchanged. `sonnet-high` stays the default leaf for now, to be revisited after real use.
- **Opus 5.5 at high (54 @ $1.82) beats Astra at max (~53 @ ~$3.3)** on both score and cost, and sits on the Pareto line with Opus xhigh and max. Max scores highest on AA's index (58 vs xhigh's 56) but loses to xhigh on Terminal-Bench (65% vs 66.5%) at roughly 1.7x the cost ($5.98 vs $3.46), which is why `opus-xhigh`, not max, is the top Opus route. Sonnet 5.5 and Fable points remain above the frontier on cost; that is expected for subscription-billed routes and is not a reason to move Claude proposers off the Claude leg.

**GPT-6.1 Sol, measured by AA** (page https://artificialanalysis.ai/models/releases/gpt-6-1-sol, read 2026-10-01). Intelligence Index @ cost per index task (output speed): low 42 @ $0.13 (60 t/s); medium 48 @ $0.21 (54 t/s); high 50 @ $0.32 (60 t/s); xhigh 51 @ $0.39 (55 t/s); max 52 @ $0.72 (64 t/s). Context 1M on AA. AA lists GPT-6 Astra at 53 (max). xhigh is +1 over high for ~22% more cost, so `sol-xhigh` is a cheap +1 when it matters but `sol-high` stays the routine pick.

**Task-specific vendor benchmarks.** From OpenAI's GPT-6.1 Sol announcement charts, exact values from the page's embedded chart data (score @ cost/task; OpenAI's harness and costs, not AA's):

| Benchmark, model | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| DeepSWE v1.1, GPT-6.1 Sol | 64.4% @ $0.17 | 73.0% @ $0.42 | 75.2% @ $0.65 | 71.9% @ $0.79 | 71.9% @ $1.57 |
| DeepSWE v1.1, GPT-6 Astra | 67.0% @ $1.60 | 72.8% @ $3.08 | 73.2% @ $3.92 | 74.1% @ $4.43 | 73.2% @ $7.50 |
| OSWorld 2.0 offline, GPT-6.1 Sol | 59.0% @ $0.43 | 66.8% @ $0.77 | 69.6% @ $0.96 | 69.4% @ $1.05 | 71.4% @ $1.27 |
| OSWorld 2.0 offline, GPT-6 Astra | 62.2% @ $2.72 | 69.3% @ $5.36 | 70.0% @ $6.91 | 71.3% @ $7.49 | 73.5% @ $9.44 |
| AutomationBench 1.0.6, GPT-6.1 Sol | 24.7% @ $0.16 | 31.7% @ $0.19 | 33.2% @ $0.23 | 35.5% @ $0.25 | 36.1% @ $0.30 |
| AutomationBench 1.0.6, GPT-6 Astra | 30.3% @ $1.08 | 34.1% @ $1.27 | 37.1% @ $1.44 | 39.0% @ $1.50 | 41.4% @ $1.73 |
| AutomationBench 1.0.6, Opus 5.5 w/ fallbacks | 24.2% @ $0.51 | 29.5% @ $0.65 | 33.0% @ $0.71 | 35.8% @ $0.89 | 42.5% @ $1.44 |
| GDP.pdf, GPT-6.1 Sol | 27.0% @ $0.33 | 30.0% @ $0.34 | 32.0% @ $0.35 | 31.8% @ $0.37 | 31.0% @ $0.42 |
| GDP.pdf, GPT-6 Astra | 30.4% @ $1.70 | 30.4% @ $1.72 | 31.0% @ $1.80 | 32.2% @ $1.91 | 31.0% @ $2.08 |
| GDP.pdf, Opus 5.5 w/ fallbacks | 25.6% @ $0.76 | 25.6% @ $0.80 | 28.8% @ $0.83 | 26.6% @ $0.96 | 26.2% @ $1.55 |
| Terminal-Bench Science 0.1, GPT-6.1 Sol | 43.7% @ $1.79 | 47.6% @ $2.34 | 51.1% @ $2.76 | 53.7% @ $2.89 | 57.0% @ $5.47 |
| Terminal-Bench Science 0.1, GPT-6 Astra | 55.4% @ $11.41 | 57.4% @ $12.34 | 62.0% @ $14.95 | 60.9% @ $15.76 | 68.1% @ $23.80 |

Terminal-Bench Science Opus 5.5 w/ fallbacks: max only, 63.3% @ $23.21. Factual-error rate on difficult prompts (lower is better), GPT-6.1 Sol / Astra: low 7.7 / 6.3%, medium 6.3 / 4.4%, high 4.5 / 3.9%, xhigh 4.1 / 4.0%, max 4.6 / 3.9%. Secondary write-ups misreported some of these (for example AutomationBench medium as 35.4%); use the chart values.

## Cross-family verification

A same-family reviewer shares the proposer's blind spots, so Claude work is challenged by a GPT model and GPT work by a Claude model. No model reviews its own output. DeepSeek is the third family: use it as the challenger when the proposer's family and the GPT family have already disagreed, or when the work is metered-cheap enough that Flash is the right price for a second opinion.

| Proposer | Challenger | Escalate to |
|---|---|---|
| `opus-high`, `opus-xhigh`, `fable-*` | `gpt-astra-high` | `gpt-astra-xhigh` |
| `opus-medium` | `gpt-sol-high` | `gpt-astra-medium` |
| `sonnet-high` | `gpt-sol-high` | `gpt-astra-high` |
| `sonnet-medium` (prompts above 100k tokens) | `gpt-sol-medium` | `gpt-sol-high` |
| `haiku-low` | `gpt-luna-medium` | `gpt-sol-medium` |
| `haiku-xhigh`, `haiku-max` | `gpt-sol-medium` | `gpt-sol-high` |
| `gpt-astra-*` | `opus-high` | `opus-xhigh` |
| `gpt-sol-high`, `gpt-sol-xhigh` | `opus-high` | `opus-xhigh` |
| `gpt-sol-medium` | `opus-medium` | `opus-high` |
| `gpt-luna-*` | `haiku-xhigh` | `sonnet-high` |
| `deepseek-v4-pro-high`, `deepseek-flash-high` | `opus-high` | `gpt-sol-high` |
| `deepseek-*-medium` | `sonnet-high` | `opus-medium` |
| `deepseek-*-low` | `haiku-xhigh` | `sonnet-high` |

The `gpt-astra-high`/`gpt-astra-xhigh` challenger for Claude proposers (51/52) scores below the proposer (`opus-high` 54, `opus-xhigh` 56) — it is kept for family diversity, not strength.

`sonnet-high` (47) and `opus-medium` (~51) are both challenged by `gpt-sol-high` (AA-measured 50 @ $0.32), to save Codex quota: sol-high scores above `gpt-astra-medium` (~49.5 @ ~$1.55) at about a fifth of its cost. `sonnet-high` escalates to `gpt-astra-high` and `opus-medium` to `gpt-astra-medium`. Fallback if `gpt-sol-high` ever fails: `gpt-astra-medium`, escalating to `gpt-astra-high`, for both `sonnet-high` and `opus-medium`. AA shows `gpt-sol-xhigh` only +1 over `gpt-sol-high` (51 vs 50) for ~22% more cost, so it stays out of the routine challenger role; it is a cheap +1 when it matters.

**Go-to shape (Craig):** Opus orchestrates. Implementation: `sonnet-high` and `gpt-sol-medium`/`gpt-sol-high` are co-equal defaults; sol is not a special-case cross-family route for leaf work. Verification: the other family checks (Sonnet work by sol, sol work by Sonnet or Opus per the table above; `sonnet-high` is also an acceptable routine challenger for `gpt-sol-medium` since they are level, 47 vs 48, but the table lists `opus-medium`). Escalation: `opus-high` or astra, in either direction. Edge cases: `fable-*` is a second Claude view, not an escalation step (when `opus-high` stalls, use `opus-xhigh`); luna is cheap mechanical work, short inputs only. GPT-6.1 Sol low (42) is about `sonnet-medium` (41), but no `gpt-sol-low` route exists.

Guidance (Craig): sol is the go-to for routine cross-family checks. For the hardest problems, ones that need tenacity, or ones sol stalled on, pull in astra. Consequential challenges (`opus-high` and above), design calls, and security stay on astra.

Third-family tiebreak: when proposer and challenger disagree and the escalation rung would be the same family as one of them, use `deepseek-flash-high` for Sonnet-tier work and `deepseek-v4-pro-high` for Opus-tier work instead, and report all three positions.

Size the challenger to the cost of being wrong, not to the proposer's rank. Treat a cross-family disagreement as a finding to resolve, not a tie to split: escalate one rung and report both positions.

The review-changes skill picks its single verifier from this table, and that verifier is advised for substantial changes, not required for every change.

With the proxy down or unconfigured there is no cross-family route: use `opus-medium` for routine checks and `opus-high` otherwise; escalate to `opus-xhigh` if `opus-high` stalls. Report the check as same-family. The proxy uses the Codex subscription credential for the GPT leg, so a stale one is fixed with `codex login`, not by rerouting; the DeepSeek leg needs a configured prepaid key and answers `503` without one.

### Security routing

Security work — doing it and reviewing it — goes to `gpt-astra-*`, not a Claude route: most cybersecurity tasks on Opus 5.5 and on Fable are re-routed by Anthropic to Opus 4.8, so a Claude route reviewing GPT's security work may actually be running 4.8, not 5.5. Routine bug finding and fixing in normal development is unaffected. On Sonnet 5.5, higher-risk cybersecurity tasks visibly fall back to Sonnet 5, so security work stays on `gpt-astra-*`: no Claude route is full-strength for security. Haiku 5.5 has no fallback: a cyber-classifier decline comes back as `stop_reason: "refusal"` and stays declined, a visible failure rather than a silent downgrade, so `haiku-*` routes never run security work at all.

With the proxy down, security work loses its full-strength route: fall back to `opus-high` (or `opus-xhigh`), not Fable, and report both the same-family fallback and that the check may be running on Opus 4.8.

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
