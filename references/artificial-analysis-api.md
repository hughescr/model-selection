# Artificial Analysis Free API

Source: [Artificial Analysis API Reference](https://artificialanalysis.ai/data-api/docs). Treat the live page as authoritative when this reference and a response disagree. The free API is intended for model benchmarks, speed, and pricing. The client in `scripts/model_selection.py` currently uses only the LLM catalog endpoint.

## Authentication and Limits

- Base URL: `https://artificialanalysis.ai/api/v2`
- Header: `x-api-key: YOUR_KEY`
- LLM catalog: `GET /language/models/free`
- API errors: `401` missing/invalid key, `429` rate limit exceeded, `500` server error.
- Free API limit: 1,000 requests per day.
- Attribution to [artificialanalysis.ai](https://artificialanalysis.ai/) is required when sharing or publishing data from the free API.
- Artificial Analysis recommends stable model and creator IDs as primary identifiers. Names and slugs can change.
- Do not put API keys in client-side code or generated output. Cache responses.

## LLM Catalog Request

```bash
curl -X GET https://artificialanalysis.ai/api/v2/language/models/free \
  -H "x-api-key: YOUR_KEY"
```

The response is an object with `tier`, `intelligence_index_version`, a `pagination` object, and a `data` array. The catalog is paginated: as of this writing `pagination.page_size` is 200 and the full free-tier catalog spans 3 pages (591 models total). Pass `?page=N` (1-based) to fetch a specific page. `pagination` looks like:

```json
{"page": 1, "page_size": 200, "total_pages": 3, "has_more": true}
```

`fetch_models` in `scripts/model_selection.py` fetches every page and merges their `data` arrays into one list before caching, so downstream code always sees the complete catalog.

## LLM Record

The relevant record shape is:

```json
{
  "id": "stable-model-id",
  "name": "Model display name",
  "slug": "url-friendly-model-slug",
  "release_date": "2025-08-11",
  "model_creator": {
    "id": "stable-creator-id",
    "name": "Creator name"
  },
  "evaluations": {
    "artificial_analysis_intelligence_index": 62.9,
    "artificial_analysis_coding_index": 55.8,
    "artificial_analysis_agentic_index": 48.1
  },
  "artificial_analysis_intelligence_index_cost": {
    "total_cost": 1040.88,
    "cost_per_task": {"total_cost": 0.6912}
  },
  "pricing": {
    "price_1m_input_tokens": 1.1,
    "price_1m_output_tokens": 4.4,
    "price_1m_cache_hit_tokens": null,
    "price_1m_cache_write_tokens": null
  },
  "performance": {
    "median_output_tokens_per_second": 153.831,
    "median_time_to_first_token_seconds": 14.939,
    "median_time_to_first_answer_token_seconds": 14.939,
    "median_end_to_end_response_time_seconds": 16.2
  }
}
```

`model_creator` on the free tier carries only `id` and `name`; there is no creator `slug`.

### Stable identity

Use `id` for joins and saved decisions. Use `name` for display and `slug` for human-readable matching. The model creator fields are useful when several providers or model families share similar names.

### Evaluations

`evaluations` is an open-ended object in principle, but the free tier of `/language/models/free` currently exposes exactly three keys on every record (present with a `null` value when unmeasured): `artificial_analysis_intelligence_index`, `artificial_analysis_coding_index`, and `artificial_analysis_agentic_index`. Older cached payloads (from the retired `/data/llms/models` endpoint) may still carry granular standalone benchmarks such as `mmlu_pro`, `gpqa`, `hle`, `livecodebench`, or `scicode` — the aliasing in `TOPIC_ALIASES` keeps resolving those keys for backward compatibility with such a cache, but a fresh fetch from the free tier will not repopulate them. Do not hard-code a closed schema; a future free-tier expansion could add fields back.

Current methodology groups Intelligence Index v4.1 evaluations into Agents (34%), Coding (24%), Scientific Reasoning (24%), and General (18%). The included evaluations are GDPval-AA v2, tau3-Banking, Terminal-Bench v2.1, SciCode, AA-LCR, AA-Omniscience, Humanity's Last Exam, GPQA Diamond, and CritPt. Standalone evaluations such as LiveCodeBench, IFBench, MMLU-Pro, Global-MMLU-Lite, and MMMU Pro belong to that broader methodology but are not present as separate fields on the free-tier `evaluations` object.

`artificial_analysis_intelligence_index_cost` is a sibling field (not inside `evaluations`) describing the dollar cost of running the intelligence-index benchmark suite against the model; it is unrelated to per-token pricing.

### Pricing

Prices are USD per 1 million tokens, under `pricing`: `price_1m_input_tokens`, `price_1m_output_tokens`, `price_1m_cache_hit_tokens`, `price_1m_cache_write_tokens`. The free tier does not return a precomputed blended price (`price_1m_blended_3_to_1` was not observed on any record); the helper derives a proxy from input and output prices using `(input + 3 * output) / 4`, and prefers a `price_1m_blended_3_to_1` field directly if a payload ever includes one.

The broader Artificial Analysis methodology defines blended price and cost-per-task separately. Per-token cost does not predict a real task bill when models differ in output length, reasoning tokens, cache hits, tool calls, or retries.

### Speed and latency

Speed and latency fields live under a nested `performance` object (not top-level, as on the retired endpoint):

- `performance.median_output_tokens_per_second`: median output generation speed.
- `performance.median_time_to_first_token_seconds`: time to the first emitted token, including reasoning tokens when applicable.
- `performance.median_time_to_first_answer_token_seconds`: time to the first answer token after hidden/reasoning tokens, when measured.
- `performance.median_end_to_end_response_time_seconds`: median wall-clock time for the full response.

`scripts/model_selection.py` reads these from `performance` first and falls back to the old top-level field names so an old cached payload still renders.

The API documents a default medium prompt length of approximately 1,000 input tokens for speed and latency data unless otherwise specified. Treat speed as endpoint experience, not a hardware maximum.

## Local Cache Contract

The helper stores `.cache/llms-models.json` with:

```json
{
  "cached_at": "UTC timestamp",
  "endpoint": "https://artificialanalysis.ai/api/v2/language/models/free",
  "payload": {"tier": "free", "intelligence_index_version": "4.1", "pagination": {}, "data": []}
}
```

`payload.data` holds the merged records from every page; `payload.pagination` reflects the last page fetched and is not meaningful for re-pagination of the cached copy.

Default behavior:

- Use a cache younger than 24 hours without a request.
- `--refresh` forces a request.
- On network/API failure, use the existing cache and print a warning unless `--no-stale-if-error` is passed.
- Use `--max-age SECONDS` to set a different freshness window.
- Set `MODEL_SELECTION_CACHE_DIR` or pass `--cache-dir` to move the cache.

This design keeps request volume low, makes a recommendation reproducible, and makes stale data visible. A stale cache is a fallback, not evidence that the current leaderboard is unchanged.

## Other Documented Endpoints

The API reference also documents free media-model endpoints:

- `GET /media/text-to-image/models/free` with optional `include_categories=true`; returns Elo, rank, confidence interval, appearances, release date, and optional category breakdown.
- `GET /media/image-editing/models/free`; returns Elo, rank, confidence interval, appearances, and release date.
- `GET /media/text-to-speech/models/free`.
- `GET /media/text-to-video/models/free` with optional `include_categories=true`.
- `GET /media/image-to-video/models/free` with optional `include_categories=true`.

The reference also documents `POST /critpt/evaluate`, a separate CritPt grading gateway limited to 10 requests per 24-hour window. It requires all problems in the public set in each batch and returns accuracy, timeout rate, server timeout count, and judge error count. The model-selection skill does not call this endpoint during ordinary selection because it is for evaluating new submissions, not catalog lookup.

## Operational Warnings

- Match on stable IDs when persisting decisions; use names and slugs only for display or initial fuzzy matching.
- Never rank missing values as zero without saying so. The helper excludes missing scores from a topic fallback and leaves the score blank.
- Use confidence intervals and evaluation version where available in a source page; the free catalog may not include them per model.
- Credit Artificial Analysis in reports and link to the source page or this reference.
