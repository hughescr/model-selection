# Artificial Analysis Free API

Source: [Artificial Analysis API Reference](https://artificialanalysis.ai/api-reference). Treat the live page as authoritative when this reference and a response disagree. The free API is intended for model benchmarks, speed, and pricing. The client in `scripts/model_selection.py` currently uses only the LLM catalog endpoint.

## Authentication and Limits

- Base URL: `https://artificialanalysis.ai/api/v2`
- Header: `x-api-key: YOUR_KEY`
- LLM catalog: `GET /data/llms/models`
- API errors: `401` missing/invalid key, `429` rate limit exceeded, `500` server error.
- Free API limit: 1,000 requests per day.
- Attribution to [artificialanalysis.ai](https://artificialanalysis.ai/) is required when sharing or publishing data from the free API.
- Artificial Analysis recommends stable model and creator IDs as primary identifiers. Names and slugs can change.
- Do not put API keys in client-side code or generated output. Cache responses.

## LLM Catalog Request

```bash
curl -X GET https://artificialanalysis.ai/api/v2/data/llms/models \
  -H "x-api-key: YOUR_KEY"
```

The response is an object with a `status`, `prompt_options`, and `data` array. `prompt_options` currently describes the default speed-test prompt settings; it does not change the quality scores returned by the catalog.

## LLM Record

The relevant record shape is:

```json
{
  "id": "stable-model-id",
  "name": "Model display name",
  "slug": "url-friendly-model-slug",
  "model_creator": {
    "id": "stable-creator-id",
    "name": "Creator name",
    "slug": "creator-slug"
  },
  "evaluations": {
    "artificial_analysis_intelligence_index": 62.9,
    "artificial_analysis_coding_index": 55.8,
    "mmlu_pro": 0.791,
    "gpqa": 0.748,
    "livecodebench": 0.717
  },
  "pricing": {
    "price_1m_blended_3_to_1": 1.925,
    "price_1m_input_tokens": 1.1,
    "price_1m_output_tokens": 4.4
  },
  "median_output_tokens_per_second": 153.831,
  "median_time_to_first_token_seconds": 14.939,
  "median_time_to_first_answer_token": 14.939
}
```

### Stable identity

Use `id` for joins and saved decisions. Use `name` for display and `slug` for human-readable matching. The model creator fields are useful when several providers or model families share similar names.

### Evaluations

`evaluations` is an open-ended object. The free API can add or retire fields as Artificial Analysis changes its evaluation suite. Do not hard-code a closed schema. Common values are either normalized pass rates in `[0, 1]` or Artificial Analysis indices on a 0-100 scale. The formatter converts normalized pass rates to display percentages for derived ranking, but preserves raw values in JSON.

Current methodology groups Intelligence Index v4.1 evaluations into Agents (34%), Coding (24%), Scientific Reasoning (24%), and General (18%). The included evaluations are GDPval-AA v2, tau3-Banking, Terminal-Bench v2.1, SciCode, AA-LCR, AA-Omniscience, Humanity's Last Exam, GPQA Diamond, and CritPt. Standalone evaluations such as LiveCodeBench, IFBench, MMLU-Pro, Global-MMLU-Lite, and MMMU Pro may appear in the same `evaluations` object but are not necessarily part of the composite index.

The live catalog fetched while this skill was created exposed these evaluation keys: `artificial_analysis_coding_index`, `artificial_analysis_intelligence_index`, `artificial_analysis_math_index`, `gpqa`, `hle`, `ifbench`, `lcr`, `livecodebench`, `math_500`, `mmlu_pro`, `scicode`, `tau2`, `tau_banking`, `terminalbench_hard`, and `terminalbench_v2_1`, plus nullable values for models without a measurement. The API is open-ended: use the cache's actual keys rather than assuming this list is permanent. In particular, machine keys may omit punctuation and version separators found in benchmark names (`terminalbench_v2_1` versus `Terminal-Bench v2.1`, `aime_25` versus AIME 2025).

Read the topic reference files before interpreting a field. In particular, `gpqa`, `hle`, `critpt`, `mmlu_pro`, `livecodebench`, and `scicode` are not interchangeable measures even when all are displayed as percentages.

### Pricing

Prices are USD per 1 million tokens. Prefer `price_1m_blended_3_to_1` for the compact comparison used by this skill. The field name indicates the endpoint's blended convention; do not substitute another blend without labeling it. If the field is missing, the helper derives a proxy from input and output prices using `(input + 3 * output) / 4`.

The broader Artificial Analysis methodology defines blended price and cost-per-task separately. Per-token cost does not predict a real task bill when models differ in output length, reasoning tokens, cache hits, tool calls, or retries.

### Speed and latency

- `median_output_tokens_per_second`: median output generation speed.
- `median_time_to_first_token_seconds`: time to the first emitted token, including reasoning tokens when applicable.
- `median_time_to_first_answer_token`: time to the first answer token after hidden/reasoning tokens, when measured.

The API documents a default medium prompt length of approximately 1,000 input tokens for speed and latency data unless otherwise specified. Treat speed as endpoint experience, not a hardware maximum.

## Local Cache Contract

The helper stores `.cache/llms-models.json` with:

```json
{
  "cached_at": "UTC timestamp",
  "endpoint": "https://artificialanalysis.ai/api/v2/data/llms/models",
  "payload": {"status": 200, "data": []}
}
```

Default behavior:

- Use a cache younger than 24 hours without a request.
- `--refresh` forces a request.
- On network/API failure, use the existing cache and print a warning unless `--no-stale-if-error` is passed.
- Use `--max-age SECONDS` to set a different freshness window.
- Set `MODEL_SELECTION_CACHE_DIR` or pass `--cache-dir` to move the cache.

This design keeps request volume low, makes a recommendation reproducible, and makes stale data visible. A stale cache is a fallback, not evidence that the current leaderboard is unchanged.

## Other Documented Endpoints

The API reference also documents free media-model endpoints:

- `GET /data/media/text-to-image` with optional `include_categories=true`; returns Elo, rank, confidence interval, appearances, release date, and optional category breakdown.
- `GET /data/media/image-editing`; returns Elo, rank, confidence interval, appearances, and release date.
- `GET /data/media/text-to-speech`.
- `GET /data/media/text-to-video` with optional `include_categories=true`.
- `GET /data/media/image-to-video` with optional `include_categories=true`.

The reference also documents `POST /critpt/evaluate`, a separate CritPt grading gateway limited to 10 requests per 24-hour window. It requires all problems in the public set in each batch and returns accuracy, timeout rate, server timeout count, and judge error count. The model-selection skill does not call this endpoint during ordinary selection because it is for evaluating new submissions, not catalog lookup.

## Operational Warnings

- Match on stable IDs when persisting decisions; use names and slugs only for display or initial fuzzy matching.
- Never rank missing values as zero without saying so. The helper excludes missing scores from a topic fallback and leaves the score blank.
- Use confidence intervals and evaluation version where available in a source page; the free catalog may not include them per model.
- Credit Artificial Analysis in reports and link to the source page or this reference.
