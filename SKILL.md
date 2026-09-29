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
| `gpt-astra-medium`, `gpt-astra-high`, `gpt-astra-xhigh` | `astra-medium`, `astra-high`, `astra-xhigh` (`gpt-6-astra`) | Consequential challenge above sol (`opus-high` and up, design calls, security); the hardest or tenacity-needing problems; work sol stalled on. `astra-medium` is the escalation for `opus-medium` (and for when sol stalls); `astra-high` the escalation for `sonnet-high`. | `opus-high`, `opus-xhigh` (`astra-medium` also escalates `opus-medium`) | `medium`, `high`, `xhigh` | `medium` | `low`-`ultra` | Mixed: astra at medium (~49.5, 2026-09-28 chart) still edges GPT-6 Sol max (48), but astra max (~53 @ ~$3.3) sits below its Claude peer `opus-high` (54; chart ~53.5 @ ~$1.8) — no Astra effort reaches `opus-high`, and `opus-medium` (~51 @ ~$1.35) beats astra medium/high (~49.5 @ ~$1.55, ~51 @ ~$1.75). Astra low ~46 @ ~$0.8 is inferred (dot obscured on the chart). Route verified live 2026-09-11; catalog says 272k context. GPT-6.1 Sol (est., unmeasured: high ~49 @ ~$0.34, max ~51 @ ~$0.68) would match astra medium at a fifth to half its cost, so since 2026-09-29 (Craig's decision) `gpt-sol-high` is the routine challenger for `sonnet-high` and `opus-medium` and astra is the escalation rung; recheck when AA measures it, and revert if sol-high lands well below ~48. |
| `gpt-sol-high`, `gpt-sol-xhigh` | `sol-high`, `sol-xhigh` (`gpt-6.1-sol` since 2026-09-29: the bare alias floats to it; `sol-6` pins `gpt-6-sol`) | Routine cross-family challenger (`high`) for `sonnet-high` and `opus-medium` (since 2026-09-29, Craig's decision; `xhigh` is no longer a challenger). Multi-file GPT leaf changes (`high`); heavy work, complex debugging, long-horizon agent runs. Consequential review of `opus-high` and above stays on astra. | `sonnet-high` (capability: GPT-6 Sol xhigh ~44, max 48 vs 47; GPT-6.1 Sol est. ~49 at high and xhigh); also challenges `opus-medium`; role peer of `opus-high` | `high`, `xhigh` | `low` (not rechecked for GPT-6.1) | `low`-`ultra` for GPT-6 Sol; OpenAI lists `low`-`max` for GPT-6.1 Sol | Weak against `opus-high`: on the 2026-09-28 chart GPT-6 Sol high/xhigh (~43/~44) sit ~10 below it (54). Only GPT-6 Sol max (48, AA page) reaches `sonnet-high`, and no route runs max. GPT-6.1 Sol, which the route now runs, is est. ~49 at both high (~$0.34) and xhigh (~$0.40): at or above `sonnet-high`, still ~5 below `opus-high` — provisional, recheck when AA measures it. On these estimates `sol-high` became the routine challenger for `sonnet-high` and `opus-medium` on 2026-09-29; `sol-xhigh` adds nothing over high on OpenAI's charts. Revert if AA puts sol-high well below ~48. |
| `gpt-sol-medium` | `sol-medium` (`gpt-6.1-sol` since 2026-09-29: the bare alias floats to it; `sol-6` pins `gpt-6-sol`) | Normal GPT leaf work: the default GPT leaf route (since 2026-09-28, replacing terra). Also routine verification, or a second opinion on another agent's work. | `sonnet-medium` (capability); role peer of `opus-medium` | `medium` | `low` (not rechecked for GPT-6.1) | `low`-`ultra` for GPT-6 Sol; OpenAI lists `low`-`max` for GPT-6.1 Sol | GPT-6 Sol measured ~40 (chart 2026-09-28): about level with `sonnet-medium` (41) and ~11 below its role peer `opus-medium` (~51). GPT-6.1 Sol, which the route now runs, is est. ~47.5 (44.5-50) @ ~$0.22: above `sonnet-medium`, level with `sonnet-high` (47), ~3.5 below `opus-medium` — provisional, recheck when AA measures it. |
| `gpt-luna-medium` | `luna-medium` (`gpt-6-luna`: proxy lists it as of 2026-09-28) | Bounded work with objective checks: extraction, classification, mechanical refactors. Short inputs only. | `sonnet-medium` | `medium` | `medium` | `low`-`max` | Strong on positioning and on the long-context limit; the peering is a cost-and-role match. |
| `gpt-luna-low` | `luna-low` (`gpt-6-luna`: proxy lists it as of 2026-09-28) | Cheap mechanical work and summaries. | `haiku-basic` | `low` | `medium` | `low`-`max` | Weak: no published head-to-head against Haiku, and the index puts luna well above it. A cost peer, not a capability peer. |
| `deepseek-flash-low`, `deepseek-flash-medium`, `deepseek-flash-high` | `deepseek-flash` (DeepSeek V4.1 Flash) plus frontmatter effort | The default DeepSeek route and the cheapest third-family challenger; peers Haiku, `sonnet-medium`, and `sonnet-high` by tier. | `haiku-*`, `sonnet-medium`, `sonnet-high` | `low`, `medium`, `high` | DeepSeek's own default | forwarded unvalidated; `low`-`high` exercised | Index position is strong; the per-tier peering is inferred from the single max-effort point AA publishes. Weaker since Sonnet 5.5 (2026-09-28): Flash max (39.5) is now below `sonnet-medium` (41) and well below `sonnet-high` (47), so the flash tier peering with Sonnet is a cost match, not a capability match. |
| `deepseek-v4-pro-low`, `deepseek-v4-pro-medium`, `deepseek-v4-pro-high` | `deepseek-v4-pro` (DeepSeek V4 Pro 0813) plus frontmatter effort | Only when a task needs something the index does not measure; on the index Flash dominates it. No image input. | `sonnet-medium`, `opus-medium`, `opus-high` | `low`, `medium`, `high` | DeepSeek's own default | forwarded unvalidated; `low`-`high` exercised | The peering is a role placeholder, not evidence: AA puts Pro below Flash at over twice the cost. |

Facts that constrain these routes:

- **Context is 272k tokens on the Codex leg, not the 1M the API docs advertise.** Never plan a larger task onto a `gpt-*` route; the catalog gives astra the same 272k. GPT-6.1 Sol's API docs say 1.05M (922k max input); its Codex-leg window is unverified, so keep assuming 272k. DeepSeek windows are unverified.
- **Keep luna off long context.** Its long-context recall is 41.3% against sol's 91.5%, so it degrades quietly rather than failing.
- **On the Codex leg a suffixed model name is the only way to set effort.** Frontmatter `effort` never reaches that leg: utraque's `chooseEffort` reads a model-name suffix, then two `Options` fields no non-test code assigns, then the catalog default. So agent files send `sol-high`, `luna-low`, and the frontmatter `effort` key is bookkeeping for the CLAUDE.md pin rule. A bare alias silently drops to the proxy default — `low` for sol, the worst case on a consequential-review route.
- **On the DeepSeek leg the model name must be exact** (`deepseek-flash`, `deepseek-v4-pro`; a suffix like `deepseek-flash-high` is rejected as unrecognised) and effort travels in the frontmatter key instead. The proxy forwards the effort field as-is, so a value DeepSeek does not honor fails or degrades upstream rather than at the proxy.
- **`ultra` is not a valid frontmatter effort.** Reach it only via a suffixed name (`sol-ultra`), at roughly triple the cost for one to three points. OpenAI documents `ultra` as sol-only; the live catalog also accepts it on terra, which no public source confirms (terra has no route since 2026-09-28). OpenAI's GPT-6.1 Sol docs list `low`-`max` with no `ultra`, so `sol-ultra` may now fail or be clamped; unverified.
- The proxy accepts a bare alias (`sol`), a pinned name (`sol-5.6`, `sol-6`, `sol-6.1`), a raw slug (`gpt-5.6-sol`), or an effort suffix (`sol-high`); the model picker shows these as `anthropic-compat.<alias>`. Whether a pinned name takes an effort suffix (`sol-6-high`) is unverified.
- **Do not route to `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, or `gpt-5.3-codex-spark`.** The first three retire 2026-08-31 and OpenAI's migration advice is terra and luna (terra has no route here since 2026-09-28; use sol or luna); spark is excluded by choice and its agent was removed 2026-09-11. Do not route to `codex-auto-review`: hidden and undocumented.
- **GPT-6 Sol and Luna launched 2026-09-22** (`gpt-6-sol`, `gpt-6-luna`; Codex, Plus/Pro/Business/Enterprise/Edu). No GPT-6 Terra — `gpt-5.6-terra` is still current but has had no route since 2026-09-28; GPT-6 Astra is unchanged (launched earlier in September). API price per 1M tokens, input/output: Sol $2/$10, Luna $0.10/$0.50 — both half of GPT-5.6's promotional pricing. Context window and effort list are not published. The luna long-context warning above (41.3% recall) was measured on GPT-5.6 Luna; treat it as unverified for GPT-6 Luna and keep it in force until measured.
- **GPT-6.1 Sol launched 2026-09-29** (`gpt-6.1-sol`; Codex and ChatGPT Work for Plus/Pro/Business/Enterprise/Edu, not yet ChatGPT Chat; API Responses, Chat Completions, Batch). Same $2/$10 per 1M input/output as GPT-6 Sol; cached input $0.10 (half GPT-6 Sol's). API docs: 1.05M context (922k max input), 128k max output, efforts `low` / `medium` (default) / `high` / `xhigh` / `max`, knowledge cutoff 2026-04-30. An "Ultrafast" mode (up to 8x token speed in Codex) is promised "in the coming days". No GPT-6.1 Luna or Astra. AA has not measured it yet; estimates are in the 2026-09-29 update below.
- **utraque's bare aliases float to the newest version carrying a codename** (`internal/router/registry.go`), so once the proxy's catalog includes GPT-6, `gpt-sol-*` and `gpt-luna-*` run GPT-6 with no agent-file change; the retired `gpt-terra-*` routes stayed on 5.6; pinned `sol-5.6`/`luna-5.6` keep the old models. Caveat: utraque reads the Codex CLI version only at startup and sends it as `client_version` on catalog fetches, and the backend withholds GPT-6 Sol/Luna from older clients — on 2026-09-22 the running proxy still sent `0.155.0-alpha.9` while the CLI was `0.155.0`, so it did not yet list them (fix in progress). Check `/v1/models` for `sol-6`/`luna-6` (or equivalent) before assuming a route runs GPT-6. **Checked 2026-09-28:** `/healthz` ok (`client_version` `0.155.0-alpha.16.3`, catalog loaded, 9 models); `/v1/models` lists `sol`, `sol-6`, `luna`, `luna-6`, `astra`, `astra-6` as GPT-6 and pinned `sol-5.6`, `luna-5.6`, `terra`/`terra-5.6`, so bare and suffixed `sol`/`luna` should resolve to GPT-6. Listing only: no request was sent, so serving is not verified. **Checked 2026-09-29:** `/healthz` ok (`client_version` `0.159.0`, catalog loaded, 10 models; bare aliases `5.5`, `astra`, `luna`, `sol`, `terra`); `/v1/models` lists `sol` and `sol-6.1` as GPT-6.1-Sol, `sol-6` as GPT-6-Sol, `sol-5.6` as GPT-5.6-Sol, and luna/astra/terra unchanged from 2026-09-28. So every `gpt-sol-*` route should now run GPT-6.1 Sol with no agent-file change, and the measured GPT-6 Sol figures in this skill describe the previous model; `sol-6` would pin it. Listing only: no request was sent, so serving and the proxy's default effort for GPT-6.1 are not verified.

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
| Claude Sonnet 5 (medium; superseded by Sonnet 5.5 on 2026-09-28) | 28.5 | $1 | no |
| GPT-5.6 Luna (medium) | 25.5 | $0.013 | yes |

**2026-09-28 AA chart** ("Intelligence Index vs. Cost per Intelligence Index Task"). Newer than the table above, which stays as history. It supplies measured costs for Opus 5.5 and GPT-6 Sol/Luna/Astra, which replace the estimates below. Readings marked ~ are approximate chart readings; unmarked figures are exact AA page values. The Pareto line runs through Opus 5.5 medium, high, xhigh, and max; GPT-6 Sol max (48 @ $1.06); and GPT-6 Luna low through xhigh. No Sonnet 5.5 point is on it. Two faded Pareto points (~38 @ ~$0.063, ~46.5 @ ~$0.13) are Xiaomi models, not routable. GPT-5.6 Terra is not on this chart; its last AA figures stand (max 42 @ $1.40, medium 30.5 @ $0.19).

**2026-09-22 update — Opus 5.5.** `claude-opus-5-5` ships with 1M context (AA) and efforts `low` / `medium` (default) / `high` / `xhigh` / `max`; the `opus` alias now resolves to it (this session runs on it; not independently verified from a spawned agent). Anthropic says it "performs at the level of Claude Fable 5.1 on most work." AA Intelligence Index v4.3.2 by effort (the Opus 5.5 column is authoritative for score; the last column is the 2026-09-28 chart, approximate, so its scores differ slightly):

| Effort | Opus 5.5 | Fable 5.1 | GPT-6 Astra | Opus 5 | Opus 5.5 chart, index @ cost/task |
|---|---|---|---|---|---|
| max | 58 | 53 | 53 | 51 | ~57.5 @ ~$6 |
| xhigh | 56 | 53 | 52 | 51 | ~56 @ ~$3.5 |
| high | 54 | 51 | 51 | 49 | ~53.5 @ ~$1.8 |
| medium | 51 | 49 | 50 | – | ~51 @ ~$1.35 |
| low | – | 47 | 46 | – | ~42.5 @ ~$0.55 |

AA's page showed Opus 5.5 cost as "N/A" on 2026-09-22; the chart costs above replace the estimate made then (Terminal-Bench cost × 0.38; ~$1.10 / $1.45 / $2.75 / $4.25 for medium/high/xhigh/max), which ran ~20-30% low. Fable 5.1 (max) is $7.63 on AA's 2026-09-22 page.

Terminal-Bench 4.0 (Anthropic's chart; GPT figures as OpenAI reported them): Opus 5.5 low 38.5%, medium 57.5%, high 64%, xhigh 66.5%, max 65%.

Most cybersecurity tasks on Opus 5.5 and on Fable are re-routed by Anthropic to Opus 4.8; routine bug finding and fixing in normal development is unaffected — see Security routing below.

Sonnet 5.5 shipped 2026-09-28 (update below). Haiku 5.5 is still due "in the coming weeks" (Anthropic) — recheck `haiku-basic` and its pairings then.

Sonnet 5.5 low (index 36 @ $0.41/task, AA-measured) is a candidate stand-in for basic work if Haiku 4.5 underperforms — note only, no route.

**2026-09-22 update — GPT-6 Sol and Luna.** OpenAI compared the new models to Opus 5, not Opus 5.5. Selected claims: AutomationBench — Sol xhigh 33.2% at $0.27/task, Astra low 30.3%, Opus 5 max 26.9% (for reference: Opus 5.5 40.0%, Astra max 41.4%, from Anthropic's page). DeepSWE — Sol max 68.8%, Luna max 66.6% (about Opus 5 at medium). OSWorld 2.0 offline — Sol xhigh 60.5% vs Opus 5 medium 60.3%.

Measured 2026-09-28 (AA chart; index @ cost/task; ~ = approximate reading, unmarked = AA page). The 2026-09-22 cost estimates (AA cost ÷ OpenAI DeepSWE-chart cost × 0.37-0.40) are shown for comparison:

| Effort | GPT-6 Sol (est.) | GPT-6 Luna (est.) | GPT-6 Astra |
|---|---|---|---|
| low | ~34 @ ~$0.13 | ~21 @ ~$0.006 | ~46 @ ~$0.8 (inferred: dot obscured by a chart label) |
| medium | ~40 @ ~$0.25 (est. $0.15) | ~29.5 @ ~$0.018 (est. $0.02) | ~49.5 @ ~$1.55 |
| high | ~43 @ ~$0.38 (est. $0.24) | ~32 @ ~$0.029 (est. $0.03) | ~51 @ ~$1.75 |
| xhigh | ~44 @ ~$0.55 (est. $0.37) | ~34 @ ~$0.043 (est. $0.04) | ~52.5 @ ~$2.35 |
| max | 48 @ $1.06 (est. ~$1.00) | ~37.5 @ ~$0.068 (est. $0.08) | ~53 @ ~$3.3 |

Findings (measured, not estimated; routing consequences are in the tables and bullets below):

- **The cost method held for Luna and for Sol max, but Sol medium/high/xhigh ran ~40% low.** Do not reuse the DeepSWE ratio for Sol below max.
- **The "expected mid-40s" for GPT-6 Sol medium was wrong: it is ~40**, level with GPT-5.6 Sol medium (39.5 @ $0.5) at half the cost, and below Sonnet 5.5 high (47) — so Sol medium does not challenge `sonnet-high`.
- **GPT-6 Sol dominates GPT-5.6 Terra on score:** Sol high (~43 @ ~$0.38) beats Terra max (42 @ $1.40) at under a third of the cost; Sol medium (~40 @ $0.25) beats Terra medium (30.5 @ $0.19) on score for ~$0.06 more. The `gpt-terra-*` retirement condition noted 2026-09-22 is therefore **met on AA**. **Retired 2026-09-28 (Craig's decision):** `gpt-terra-medium`/`gpt-terra-high` (which sent `terra-medium`/`terra-high`) are deleted and the default GPT leaf is now `gpt-sol-medium` (`gpt-sol-high` for multi-file changes). `gpt-5.6-terra` is still reachable on the proxy as `terra`, but no route uses it. `/v1/models` lists `sol`/`sol-6` as GPT-6-Sol (2026-09-28, listing only), so confirm it serves GPT-6 before relying on the Sol score for leaf work.
- GPT-6 Sol max (48 @ $1.06, on the Pareto line) is level with Sonnet 5.5 high (47 @ $1.08) and below Opus 5.5 medium (~51 @ ~$1.35), high, and Astra max (~53 @ ~$3.3) — a cheaper frontier point, not a replacement.
- GPT-6 Luna max (~37.5 @ ~$0.068) roughly matches GPT-5.6 Luna max (37.5 @ $0.19) at about a third of the cost; Luna low through xhigh are on the Pareto line.

**2026-09-28 update — Sonnet 5.5.** `claude-sonnet-5-5` (all platforms) ships with 1M context (AA), API price $2/$10 per 1M input/output (cache read $0.20, write $2.50), and efforts `low` / `medium` / `high` / `xhigh` / `max`: default `medium` in Claude Code and apps, `high` on the API. The `sonnet` alias now resolves to it (verified from a spawned `sonnet-high` agent on 2026-09-28), so `sonnet-high` and `sonnet-medium` run Sonnet 5.5 unchanged. Anthropic claims 30%+ faster than Sonnet 5, up to 30% cheaper for most work. AA Intelligence Index, measured 2026-09-28 (with default fallback), and Anthropic's chart readings (approximate; cost is Anthropic's per-attempt, not AA's):

| Sonnet 5.5 effort | AA index @ AA cost/task | Terminal-Bench 4.0 (~, $/attempt) | FrontierCode v1.1 (~, $/task) | CursorBench 4.0 (~, $/task) |
|---|---|---|---|---|
| low | 36 @ $0.41 | 20% @ $0.75 | 29% @ $0.19 | 36% @ $0.5 |
| medium | 41 @ $0.59 | 29% @ $0.85 | 36.5% @ $0.24 | 39% @ $0.7 |
| high | 47 @ $1.08 | 43% @ $1.9 | 49.4% @ $0.43 | 48% @ $1.7 |
| xhigh | 52 @ $2.74 | 61.5% @ $5.3 | 52.2% @ $1.6 | 53% @ $3.8 |
| max | 56 @ $7.60 | 70.6% @ $12.7 | 46.2% @ $21 | 55.5% @ $9.7 |

Opus 5.5 on the same charts (Anthropic's, approximate; low / medium / high / xhigh / max): Terminal-Bench 38.5% @ $1.3, 57.5% @ $2.9, 64% @ $3.9, 66.5% @ $7.3, 65% @ $11.5. FrontierCode 47.3% @ $0.42, 54.6% @ $0.8, 54% @ $1.1, 51.4% @ $2.2, 54.4% @ $6. CursorBench 43.7% @ $1.2, 52.5% @ $2.9, 56% @ $3.9, 56% @ $7, 57.8% @ $13. Sonnet 5 best on Terminal-Bench was 10.3%. Sonnet 5.5 max is the top Terminal-Bench point above every Opus 5.5 effort, but at $12.7. FrontierCode max scores below xhigh because at max Sonnet 5.5 more often ran Claude Code's code-review skill (many sub-agents), causing timeouts or out-of-scope edits (Anthropic footnote). Competitors' best: GPT-6 Sol 49.3% on FrontierCode, GPT-5.6 Sol 41.7% on CursorBench. Single-effort Sonnet 5.5 vs Opus 5.5: GDPval-AA v2.1 1844 vs 1846, OSWorld 2.1 80.1% vs 81.8%, HLE with tools 64.5% vs 67.7%.

Security: on Sonnet 5.5, higher-risk cybersecurity tasks visibly fall back to Sonnet 5; routine bug finding and fixing is unaffected — see Security routing below.

What follows from it:

- **Astra at medium still beats sol at max, but narrowly now.** 2026-09-11 (GPT-5.6 Sol): by about three index points at well under its cost. 2026-09-28 chart (GPT-6 Sol max): ~49.5 @ ~$1.55 vs 48 @ $1.06, so 1.5 points for ~46% more cost. Astra at max matches Fable 5.1 at max. `gpt-astra-medium` is still the cheapest route above sol and the natural consequential challenger. (Written 2026-09-28: sol at high or xhigh was then the fallback; since 2026-09-29, on GPT-6.1 Sol estimates, `gpt-sol-high` is the routine challenger and astra the escalation — see Cross-family verification.)
- **Flash is the DeepSeek default, with a narrower edge.** 2026-09-11: V4.1 Flash at max ties GPT-5.6 Sol at medium on the index at roughly half the cost, and sits above luna at max. GPT-6 Sol medium (~40 @ ~$0.25) now matches Flash (39.5 @ $0.28) on score at slightly lower AA cost, so Flash's advantage is metered-vs-subscription billing, not the index. V4 Pro is below Flash and costs over twice as much, so route to it only for a reason the index does not capture.
- **Terra at medium is dominated by luna at max.** 2026-09-11: same cost, GPT-5.6 Luna max 37.5 @ $0.19. 2026-09-28: GPT-6 Luna max (~37.5 @ ~$0.068) has the higher score at about a third of Terra medium's cost ($0.19), and GPT-6 Sol medium also beats it on score. Terra was retired 2026-09-28 (Craig's decision; see above), so this is history: for normal GPT leaf work use `gpt-sol-medium`; luna's long-context weakness still applies.
- **Sonnet 5.5 is a real step up from Sonnet 5 (28.5).** On AA, medium (41 @ $0.59) beats GPT-5.6 Sol medium (39.5) and DeepSeek Flash max (39.5); high (47 @ $1.08) is level with GPT-5.6 Sol max (47) and GPT-6 Sol max (48 @ $1.06). Per effort step, Sonnet 5.5 trails Opus 5.5 by about one step on Anthropic's charts (Sonnet high ≈ Opus low, Sonnet xhigh ≈ Opus medium, approximate) at lower cost per step. Its value on the Claude leg is still harness fit and the Max subscription.
- **No `sonnet-xhigh` or `sonnet-max` route.** Opus 5.5 high dominates Sonnet 5.5 xhigh: AA 54 (chart ~53.5) @ ~$1.8 vs 52 @ $2.74; Terminal-Bench ~64% vs ~61.5% at lower cost per attempt ($3.9 vs $5.3); CursorBench ~56% vs ~53% at about the same cost ($3.9 vs $3.8). Opus xhigh (56 @ ~$3.5) ties Sonnet max (56 @ $7.60) at under half the cost. Anthropic-chart readings are approximate. Sonnet max tops Terminal-Bench but at ~$12.7 and scores below xhigh on FrontierCode.
- **Open question, not a decision: is `sonnet-high` still the right default leaf?** On the 2026-09-28 AA chart, Opus 5.5 medium (~51 @ ~$1.35) beats Sonnet 5.5 high (47 @ $1.08): +4 points for ~25% more cost. Opus 5.5 low (~42.5 @ ~$0.55) beats Sonnet 5.5 medium (41 @ $0.59) outright, and no Sonnet 5.5 point is on the Pareto line. Anthropic's own coding charts (FrontierCode, CursorBench) favour Sonnet more than AA does. Craig decided on 2026-09-28 to keep `sonnet-high` as the default leaf for now and revisit after real use.
- **Opus 5.5 at high (~53.5-54 @ ~$1.8) beats Astra at max (~53 @ ~$3.3)** on both score and cost, and sits on the Pareto line with Opus medium, xhigh, and max — the first Claude points to do so on this chart. Max scores highest on AA's index (58 vs xhigh's 56) but loses to xhigh on Terminal-Bench (65% vs 66.5%) at roughly 1.7x the cost (~$6 vs ~$3.5), which is why `opus-xhigh`, not max, is the top Opus route. Sonnet 5.5 and Fable points remain above the frontier on cost; that is expected for subscription-billed routes and is not a reason to move Claude proposers off the Claude leg.

**2026-09-29 update — GPT-6.1 Sol (estimates; AA has not measured it).** Launch facts are in the route constraints above. On 2026-09-29 AA had no GPT-6.1 Sol entry (model page 404; its GPT-6 Sol releases page lists only GPT-6 Sol, with xhigh 44 @ $0.52 and max 48 @ $1.05, used as the anchors below). OpenAI's announcement charts, exact values from the page's embedded chart data (score @ cost/task; OpenAI's harness and costs, not AA's):

| Benchmark, model | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| DeepSWE v1.1, GPT-6.1 Sol | 64.4% @ $0.17 | 73.0% @ $0.42 | 75.2% @ $0.65 | 71.9% @ $0.79 | 71.9% @ $1.57 |
| DeepSWE v1.1, GPT-6 Sol | 37.2% @ $0.16 | 56.6% @ $0.38 | 65.3% @ $0.64 | 66.6% @ $1.00 | 68.8% @ $2.74 |
| DeepSWE v1.1, GPT-6 Astra | 67.0% @ $1.60 | 72.8% @ $3.08 | 73.2% @ $3.92 | 74.1% @ $4.43 | 73.2% @ $7.50 |
| OSWorld 2.0 offline, GPT-6.1 Sol | 59.0% @ $0.43 | 66.8% @ $0.77 | 69.6% @ $0.96 | 69.4% @ $1.05 | 71.4% @ $1.27 |
| OSWorld 2.0 offline, GPT-6 Sol | 43.9% @ $1.01 | 54.0% @ $1.38 | 58.3% @ $1.71 | 60.5% @ $2.30 | 64.4% @ $3.37 |
| OSWorld 2.0 offline, GPT-6 Astra | 62.2% @ $2.72 | 69.3% @ $5.36 | 70.0% @ $6.91 | 71.3% @ $7.49 | 73.5% @ $9.44 |
| AutomationBench 1.0.6, GPT-6.1 Sol | 24.7% @ $0.16 | 31.7% @ $0.19 | 33.2% @ $0.23 | 35.5% @ $0.25 | 36.1% @ $0.30 |
| AutomationBench 1.0.6, GPT-6 Sol | 21.2% @ $0.19 | 26.9% @ $0.21 | 31.2% @ $0.24 | 33.2% @ $0.28 | 32.0% @ $0.34 |
| AutomationBench 1.0.6, GPT-6 Astra | 30.3% @ $1.08 | 34.1% @ $1.27 | 37.1% @ $1.44 | 39.0% @ $1.50 | 41.4% @ $1.73 |
| AutomationBench 1.0.6, Opus 5.5 w/ fallbacks | 24.2% @ $0.51 | 29.5% @ $0.65 | 33.0% @ $0.71 | 35.8% @ $0.89 | 42.5% @ $1.44 |
| GDP.pdf, GPT-6.1 Sol | 27.0% @ $0.33 | 30.0% @ $0.34 | 32.0% @ $0.35 | 31.8% @ $0.37 | 31.0% @ $0.42 |
| GDP.pdf, GPT-6 Sol | 21.8% @ $0.33 | 25.4% @ $0.34 | 28.0% @ $0.35 | 23.8% @ $0.37 | 24.8% @ $0.43 |
| GDP.pdf, GPT-6 Astra | 30.4% @ $1.70 | 30.4% @ $1.72 | 31.0% @ $1.80 | 32.2% @ $1.91 | 31.0% @ $2.08 |
| GDP.pdf, Opus 5.5 w/ fallbacks | 25.6% @ $0.76 | 25.6% @ $0.80 | 28.8% @ $0.83 | 26.6% @ $0.96 | 26.2% @ $1.55 |
| Terminal-Bench Science 0.1, GPT-6.1 Sol | 43.7% @ $1.79 | 47.6% @ $2.34 | 51.1% @ $2.76 | 53.7% @ $2.89 | 57.0% @ $5.47 |
| Terminal-Bench Science 0.1, GPT-6 Sol | 9.2% @ $3.00 | 14.5% @ $4.41 | 14.6% @ $4.63 | 25.3% @ $6.77 | 27.6% @ $12.18 |
| Terminal-Bench Science 0.1, GPT-6 Astra | 55.4% @ $11.41 | 57.4% @ $12.34 | 62.0% @ $14.95 | 60.9% @ $15.76 | 68.1% @ $23.80 |

Terminal-Bench Science Opus 5.5 w/ fallbacks: max only, 63.3% @ $23.21. Factual-error rate on difficult prompts (lower is better), GPT-6.1 / GPT-6 Sol / Astra: low 7.7 / 11.4 / 6.3%, medium 6.3 / 6.9 / 4.4%, high 4.5 / 5.1 / 3.9%, xhigh 4.1 / 4.5 / 4.0%, max 4.6 / 4.6 / 3.9%. Secondary write-ups misreported some of these (for example AutomationBench medium as 35.4%); use the chart values.

Estimated AA index and cost per task for GPT-6.1 Sol (~ = estimate, not measured; range in brackets):

| Effort | GPT-6 Sol (AA, measured) | GPT-6.1 Sol index (est.) | GPT-6.1 Sol cost/task (est.) |
|---|---|---|---|
| low | 34 @ $0.13 | ~42.5 (37-45.5) | ~$0.11 ($0.08-0.14) |
| medium | 40 @ $0.25 | ~47.5 (44.5-50) | ~$0.22 ($0.14-0.28) |
| high | 43 @ $0.38 | ~49 (45-51) | ~$0.34 ($0.23-0.38) |
| xhigh | 44 @ $0.52 | ~49 (46-51) | ~$0.40 ($0.24-0.48) |
| max | 48 @ $1.05 | ~51 (49-52.5) | ~$0.68 ($0.47-0.92) |

- **Index method:** each measured GPT-6 Sol AA point shifted by the GPT-6 → 6.1 Sol gain on DeepSWE, OSWorld and AutomationBench, converted at that benchmark's AA-points-per-point slope fitted two ways (along GPT-6 Sol's effort curve; across the GPT-6 Sol, Astra and, where charted, Opus 5.5 points); estimate = mean of the six, range = min-max. GDP.pdf (not monotone in effort) and Terminal-Bench Science (GPT-6 Sol anomalously low, implying AA 55-65) were dropped.
- **Cost method:** GPT-6 Sol's AA cost × the median GPT-6.1/GPT-6 Sol cost ratio at the same effort across OpenAI's six cost charts (per-token price is unchanged, so it is a token ratio); range = the middle four ratios, widened to include the per-effort DeepSWE ratio. This applies the 2026-09-22 lesson: the flat DeepSWE ratio (×0.37-0.40) ran ~40% low for Sol below max — GPT-6 Sol's measured AA/DeepSWE cost ratio falls from 0.80 at low to 0.38 at max — so it is not used; flat ×0.38 would give $0.07 / $0.16 / $0.25 / $0.30 / $0.60 here.
- **OSWorld is the only benchmark that places GPT-6 Sol and Astra on AA consistently** (fit error ~0.5 point); alone it gives ~44 / 48.5 / 50.5 / 50 / 52. DeepSWE saturates at 73-75% (Astra max scores below Astra xhigh); AutomationBench underpredicts Astra and Opus 5.5 by 3-6 points.
- **The risk is to the downside.** OpenAI chose agentic benchmarks with the biggest gains, while AA also weighs knowledge and reasoning evals; the factuality chart barely moved above low effort (6.9 → 6.3% medium, 4.6 → 4.6% max).
- **GPT-6.1 Sol xhigh is no better than high on most charts** (DeepSWE 71.9% vs 75.2%, OSWorld 69.4% vs 69.6%, GDP.pdf 31.8% vs 32.0%) at 5-20% more cost; only AutomationBench and Terminal-Bench Science still rise. Treat `sol-xhigh` as no stronger than `sol-high` until AA says otherwise.

Routing consequences on these estimates (recheck when AA measures it). Items marked "applied 2026-09-29 (Craig's decision)" changed the cross-family table; the rest are notes only:

- **Every `gpt-sol-*` route now runs GPT-6.1 Sol** (proxy listing 2026-09-29), so the measured GPT-6 Sol numbers in the tables describe the previous model.
- `gpt-sol-medium` (~47.5) would sit above its capability peer `sonnet-medium` (41) even at the bottom of its range, level with `sonnet-high` (47), and ~3.5 below its role peer `opus-medium` (~51), not ~11.
- `gpt-sol-xhigh` would reach `sonnet-high` (~49 vs 47) instead of trailing it, and `gpt-sol-high` does the same for less. **Applied 2026-09-29 (Craig's decision):** `gpt-sol-high` replaced `gpt-sol-xhigh` as the `sonnet-high` challenger, escalating to `gpt-astra-high` instead of `gpt-astra-medium` (which would add almost nothing on score).
- Sol could match `gpt-astra-medium` (~49.5 @ ~$1.55) at high (~49 @ ~$0.34) and pass it at max (~51 @ ~$0.68), but no route runs max, and astra keeps the security role. **Applied 2026-09-29 (Craig's decision):** `gpt-sol-high` replaced `gpt-astra-medium` as the `opus-medium` challenger, with `gpt-astra-medium` as its escalation rung; astra keeps `opus-high` and above, design calls, and security.
- Sol stays ~5 below `opus-high` (54) at its best routed effort; astra remains the challenger for `opus-high`, `opus-xhigh` and `fable-*`.
- GPT-6.1 Sol medium (~47.5 @ ~$0.22) would beat DeepSeek V4.1 Flash max (39.5 @ $0.28) outright; Flash's case is metered billing and third-family diversity only.

## Cross-family verification

A same-family reviewer shares the proposer's blind spots, so Claude work is challenged by a GPT model and GPT work by a Claude model. No model reviews its own output. DeepSeek is the third family: use it as the challenger when the proposer's family and the GPT family have already disagreed, or when the work is metered-cheap enough that Flash is the right price for a second opinion.

| Proposer | Challenger | Escalate to |
|---|---|---|
| `opus-high`, `opus-xhigh`, `fable-*` | `gpt-astra-high` | `gpt-astra-xhigh` |
| `opus-medium` | `gpt-sol-high` | `gpt-astra-medium` |
| `sonnet-high` | `gpt-sol-high` | `gpt-astra-high` |
| `sonnet-medium` | `gpt-sol-medium` | `gpt-sol-high` |
| `haiku-basic` | `gpt-luna-low` | `gpt-luna-medium` |
| `gpt-astra-*` | `opus-high` | `opus-xhigh` |
| `gpt-sol-high`, `gpt-sol-xhigh` | `opus-high` | `opus-xhigh` |
| `gpt-sol-medium` | `opus-medium` | `opus-high` |
| `gpt-luna-*` | `sonnet-medium` | `sonnet-high` |
| `deepseek-v4-pro-high`, `deepseek-flash-high` | `opus-high` | `gpt-sol-high` |
| `deepseek-*-medium` | `sonnet-high` | `opus-medium` |
| `deepseek-*-low` | `sonnet-medium` | `sonnet-high` |

Since Opus 5.5 (2026-09-22), the `gpt-astra-high`/`gpt-astra-xhigh` challenger for Claude proposers (51/52) scores below the proposer (`opus-high` 54, `opus-xhigh` 56) — it is kept for family diversity, not strength.

**Decided 2026-09-29 by Craig, on GPT-6.1 Sol estimates (AA has not measured it):** `sonnet-high` (47) and `opus-medium` (~51) are both challenged by `gpt-sol-high` (est. ~49 @ ~$0.34, range 45-51), to save Codex quota: sol-high costs about a fifth of `gpt-astra-medium` (~49.5 @ ~$1.55) for about the same estimated score. `sonnet-high` escalates to `gpt-astra-high` and `opus-medium` to `gpt-astra-medium`. `gpt-sol-xhigh` is dropped from the Sonnet challenger role because GPT-6.1 Sol xhigh scores no better than high on OpenAI's charts (see the 2026-09-29 update). Recheck when AA measures GPT-6.1 Sol; revert if `gpt-sol-high` lands well below ~48 (back to `gpt-sol-xhigh` for `sonnet-high` and `gpt-astra-medium` for `opus-medium`).

Guidance (Craig): sol is the go-to for routine cross-family checks. For the hardest problems, ones that need tenacity, or ones sol stalled on, pull in astra — the same relationship as Opus being the go-to with Fable brought out when tenacity is needed. Consequential challenges (`opus-high` and above), design calls, and security stay on astra.

History: since Sonnet 5.5 and the 2026-09-28 AA chart, `sonnet-medium` (41) gets `gpt-sol-medium` (~40 measured on GPT-6 Sol, est. ~47.5 on 6.1), escalating to `gpt-sol-high`. The first Sonnet 5.5 picks were too weak: GPT-6 Sol medium (~40) is below `sonnet-high`, and terra max (42) was too. On 2026-09-28 `opus-medium` moved from `gpt-sol-medium` (~40, ~11 points below it) to `gpt-astra-medium` (~49.5); `sonnet-high` then had `gpt-sol-xhigh` (GPT-6 Sol ~44), escalating to `gpt-astra-medium`. `gpt-sol-medium` and `gpt-sol-high`/`gpt-sol-xhigh` remain proposer rows, challenged by `opus-medium` and `opus-high`; terra's proposer row was removed with the route. The DeepSeek proposer rows keep their Claude challengers, which only got stronger.

Third-family tiebreak: when proposer and challenger disagree and the escalation rung would be the same family as one of them, use `deepseek-flash-high` for Sonnet-tier work and `deepseek-v4-pro-high` for Opus-tier work instead, and report all three positions.

Size the challenger to the cost of being wrong, not to the proposer's rank. Treat a cross-family disagreement as a finding to resolve, not a tie to split: escalate one rung and report both positions.

The review-changes skill picks its single verifier from this table, and that verifier is advised for substantial changes, not required for every change.

With the proxy unavailable there is no cross-family route: fall back to a stronger same-family route and report the verification as same-family. The proxy uses the Codex subscription credential for the GPT leg, so a stale one is fixed with `codex login`, not by rerouting; the DeepSeek leg needs a configured prepaid key and answers `503` without one.

### Security routing

Security work — doing it and reviewing it — goes to `gpt-astra-*`, not a Claude route: most cybersecurity tasks on Opus 5.5 and on Fable are re-routed by Anthropic to Opus 4.8, so a Claude route reviewing GPT's security work may actually be running 4.8, not 5.5. Routine bug finding and fixing in normal development is unaffected. On Sonnet 5.5, higher-risk cybersecurity tasks visibly fall back to Sonnet 5, so security work stays on `gpt-astra-*`: no Claude route is full-strength for security.

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
