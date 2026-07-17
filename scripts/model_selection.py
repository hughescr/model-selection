#!/usr/bin/env python3
"""Fetch, inspect, rank, and format Artificial Analysis model data.

The module uses only the Python standard library so it can run inside a skill
without a virtualenv. Import its functions when a caller needs custom output,
or use the CLI for the common workflows.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable


API_BASE = "https://artificialanalysis.ai/api/v2"
LLM_ENDPOINT = "/data/llms/models"
DEFAULT_MAX_AGE = 24 * 60 * 60

# These aliases intentionally include both the names used in Artificial
# Analysis prose and the machine-oriented variants seen in API payloads.
TOPIC_ALIASES: dict[str, list[str]] = {
    "general": [
        "artificial_analysis_intelligence_index",
        "artificial_analysis_general_index",
        "mmlu_pro",
        "ifbench",
        "aa_lcr",
        "lcr",
    ],
    "coding": [
        "artificial_analysis_coding_index",
        "terminal_bench_v2_1",
        "terminal_bench",
        "scicode",
        "livecodebench",
        "swe_bench",
        "deep_swe",
        "swe_atlas_qna",
        "bigcodebench",
        "humaneval",
    ],
    "writing": [
        "artificial_analysis_agents_index",
        "gdpval_aa_v2",
        "gdpval_aa",
        "aa_briefcase",
        "harvey_lab_aa",
        "ifbench",
    ],
    "agents": [
        "artificial_analysis_agents_index",
        "gdpval_aa_v2",
        "gdpval_aa",
        "tau3_banking",
        "tau2_banking",
        "tau_banking",
        "tau2",
        "aa_briefcase",
        "apex_agents_aa",
        "automationbench_aa",
        "itbench_aa",
        "enterpriseops_gym_aa",
    ],
    "reasoning": [
        "artificial_analysis_scientific_reasoning_index",
        "hle",
        "gpqa",
        "critpt",
        "aa_lcr",
        "lcr",
        "mmlu_pro",
    ],
    "math": [
        "artificial_analysis_math_index",
        "math_500",
        "aime_2025",
        "aime_25",
        "aime",
        "frontier_math",
        "critpt",
    ],
    "science": [
        "artificial_analysis_scientific_reasoning_index",
        "gpqa",
        "hle",
        "critpt",
        "scicode",
    ],
    "multilingual": [
        "artificial_analysis_multilingual_index",
        "global_mmlu_lite",
        "global_mmlu",
    ],
    "multimodal": ["mmmu_pro", "mmmu"],
    "speed": [],
    "cost": [],
}


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_cache_dir() -> Path:
    configured = os.environ.get("MODEL_SELECTION_CACHE_DIR")
    return Path(configured).expanduser() if configured else skill_root() / ".cache"


def normalize_name(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(r"\[[^\]]+\]", "", text)
    text = re.sub(r"\b(?:1m|200k)\b", "", text)
    return re.sub(r"[^a-z0-9]+", "", text)


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=True)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def credential_path(value: str | None) -> Path:
    return Path(value).expanduser() if value else skill_root() / "creds.json"


def load_api_key(path: Path | None = None) -> str:
    env_key = os.environ.get("ARTIFICIAL_ANALYSIS_API_KEY")
    if env_key:
        return env_key
    path = path or credential_path(None)
    if not path.exists():
        raise RuntimeError(
            f"No Artificial Analysis key found. Set ARTIFICIAL_ANALYSIS_API_KEY "
            f"or provide --credentials {path}."
        )
    try:
        payload = read_json(path)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Credentials file is not valid JSON: {path}") from exc
    for key_name in ("token", "api_key", "apiKey", "key"):
        value = payload.get(key_name) if isinstance(payload, dict) else None
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise RuntimeError(f"Credentials file has no token/api_key field: {path}")


def cache_file(cache_dir: Path) -> Path:
    return cache_dir / "llms-models.json"


def cache_age_seconds(path: Path) -> float:
    try:
        return max(0.0, time.time() - path.stat().st_mtime)
    except FileNotFoundError:
        return float("inf")


def payload_data(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return [item for item in payload["data"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    raise RuntimeError("Artificial Analysis response did not contain a data list")


def fetch_models(
    *,
    cache_dir: Path | None = None,
    credentials: Path | None = None,
    max_age: float = DEFAULT_MAX_AGE,
    refresh: bool = False,
    stale_if_error: bool = True,
    timeout: float = 30,
) -> tuple[Any, dict[str, Any]]:
    """Return the API payload and cache metadata, fetching at most as needed."""
    cache_dir = cache_dir or default_cache_dir()
    path = cache_file(cache_dir)
    if path.exists() and not refresh and cache_age_seconds(path) <= max_age:
        envelope = read_json(path)
        return envelope.get("payload", envelope), {
            "source": "cache",
            "path": str(path),
            "age_seconds": cache_age_seconds(path),
            "stale": False,
        }

    try:
        key = load_api_key(credentials)
        request = urllib.request.Request(
            f"{API_BASE}{LLM_ENDPOINT}",
            headers={"x-api-key": key, "Accept": "application/json"},
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        payload_data(payload)
        envelope = {
            "cached_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "endpoint": f"{API_BASE}{LLM_ENDPOINT}",
            "payload": payload,
        }
        atomic_write_json(path, envelope)
        return payload, {"source": "network", "path": str(path), "stale": False}
    except Exception as exc:
        if stale_if_error and path.exists():
            envelope = read_json(path)
            print(f"warning: using stale cache after fetch failed: {exc}", file=sys.stderr)
            return envelope.get("payload", envelope), {
                "source": "stale-cache",
                "path": str(path),
                "age_seconds": cache_age_seconds(path),
                "stale": True,
            }
        raise


def score_value(value: Any, field: str | None = None) -> float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    value = float(value)
    if value < 0:
        return None
    if field and "index" in normalize_name(field):
        return value
    return value * 100 if 0 <= value <= 1 else value


def matching_key(evaluations: dict[str, Any], alias: str) -> str | None:
    target = normalize_name(alias)
    if target in evaluations:
        return target
    for key in evaluations:
        normalized = normalize_name(key)
        if normalized == target or target in normalized:
            return key
    return None


def metric_score(evaluations: dict[str, Any], metric: str) -> tuple[float | None, str | None]:
    key = matching_key(evaluations, metric)
    return (score_value(evaluations.get(key), key), key) if key else (None, None)


def topic_score(evaluations: dict[str, Any], topic: str) -> tuple[float | None, str]:
    if topic in {"speed", "cost"}:
        return None, topic
    aliases = TOPIC_ALIASES.get(topic, [])
    for alias in aliases:
        value, key = metric_score(evaluations, alias)
        if value is not None and alias.endswith("_index"):
            return value, key or alias
    values: list[tuple[str, float]] = []
    for alias in aliases:
        value, key = metric_score(evaluations, alias)
        if value is not None and key and key not in {existing_key for existing_key, _ in values}:
            values.append((key, value))
    if not values:
        return None, topic
    return sum(value for _, value in values) / len(values), "+".join(key for key, _ in values)


def blended_price(pricing: dict[str, Any]) -> float | None:
    direct = pricing.get("price_1m_blended_3_to_1")
    if isinstance(direct, (int, float)):
        return float(direct)
    input_price = pricing.get("price_1m_input_tokens")
    output_price = pricing.get("price_1m_output_tokens")
    if isinstance(input_price, (int, float)) and isinstance(output_price, (int, float)):
        return (float(input_price) + 3 * float(output_price)) / 4
    return None


def runtime_match(model: dict[str, Any], runtime_names: Iterable[str]) -> list[str]:
    haystack = {normalize_name(model.get("name")), normalize_name(model.get("slug"))}
    haystack.discard("")
    matches = []
    for name in runtime_names:
        candidate = normalize_name(name)
        if candidate in haystack:
            matches.append(name)
            continue
        # AA commonly publishes one row per reasoning/effort variant while
        # Codex exposes the selectable family slug. Match useful family
        # prefixes, never short generic names.
        if len(candidate) >= 6 and any(value.startswith(candidate) for value in haystack):
            matches.append(name)
            continue
        if candidate in {"opus", "sonnet", "haiku"} and any(candidate in value for value in haystack):
            matches.append(name)
    return matches


def enrich_models(
    models: list[dict[str, Any]],
    *,
    topic: str = "general",
    metric: str | None = None,
    runtime_names: Iterable[str] = (),
) -> list[dict[str, Any]]:
    result = []
    for model in models:
        evaluations = model.get("evaluations") if isinstance(model.get("evaluations"), dict) else {}
        pricing = model.get("pricing") if isinstance(model.get("pricing"), dict) else {}
        if metric:
            selected_score, selected_metric = metric_score(evaluations, metric)
        else:
            selected_score, selected_metric = topic_score(evaluations, topic)
        price = blended_price(pricing)
        cost_per_point = price / selected_score if price is not None and selected_score else None
        enriched = {
            "id": model.get("id"),
            "name": model.get("name") or model.get("slug"),
            "slug": model.get("slug"),
            "model_creator": model.get("model_creator"),
            "evaluations": evaluations,
            "pricing": pricing,
            "median_output_tokens_per_second": model.get("median_output_tokens_per_second"),
            "median_time_to_first_token_seconds": model.get("median_time_to_first_token_seconds"),
            "selected_score": selected_score,
            "selected_metric": selected_metric,
            "blended_price_per_1m_tokens": price,
            "cost_per_intelligence_point": cost_per_point,
            "cost_per_100_intelligence_points": cost_per_point * 100 if cost_per_point is not None else None,
            "runtime_matches": runtime_match(model, runtime_names),
        }
        result.append(enriched)
    return result


def parse_toml_model(path: Path) -> str | None:
    try:
        import tomllib

        with path.open("rb") as handle:
            value = tomllib.load(handle).get("model")
        return value if isinstance(value, str) else None
    except (OSError, ValueError, ModuleNotFoundError):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return None
        match = re.search(r"^model\s*=\s*[\"']([^\"']+)[\"']", text, re.MULTILINE)
        return match.group(1) if match else None


def walk_claude_models(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "model" and isinstance(child, str):
                found.append(child)
            elif key == "additionalModelOptionsCache":
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, dict) and isinstance(item.get("value"), str):
                            found.append(item["value"])
            else:
                found.extend(walk_claude_models(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(walk_claude_models(child, f"{path}[{index}]"))
    return found


def discover_runtime(runtime: str = "all", include_observed: bool = True) -> dict[str, Any]:
    home = Path.home()
    result: dict[str, Any] = {"codex": [], "claude": [], "notes": []}

    if runtime in {"all", "codex"}:
        codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser()
        cache_path = codex_home / "models_cache.json"
        config_path = codex_home / "config.toml"
        default_model = parse_toml_model(config_path) if config_path.exists() else None
        if cache_path.exists():
            try:
                cache = read_json(cache_path)
                for item in cache.get("models", []):
                    if not isinstance(item, dict) or not item.get("slug"):
                        continue
                    visible = item.get("visibility") == "list"
                    if visible or include_observed:
                        result["codex"].append({
                            "name": item.get("slug"),
                            "display_name": item.get("display_name"),
                            "status": "available" if visible else "hidden",
                            "source": str(cache_path),
                            "current": item.get("slug") == default_model,
                            "supported_in_api": item.get("supported_in_api"),
                            "reasoning_levels": [
                                x.get("effort") for x in item.get("supported_reasoning_levels", [])
                                if isinstance(x, dict) and x.get("effort")
                            ],
                        })
                fetched_at = cache.get("fetched_at")
                result["notes"].append(f"Codex model cache: {cache_path} (fetched_at={fetched_at})")
            except (OSError, ValueError, TypeError) as exc:
                result["notes"].append(f"Could not parse Codex model cache {cache_path}: {exc}")
        elif default_model:
            result["codex"].append({
                "name": default_model,
                "status": "configured",
                "source": str(config_path),
                "current": True,
            })
        else:
            result["notes"].append("No Codex model cache or configured model was found")

    if runtime in {"all", "claude"}:
        settings_path = home / ".claude" / "settings.json"
        state_path = home / ".claude.json"
        names: dict[str, dict[str, Any]] = {}

        def add(name: str, status: str, source: str, current: bool = False) -> None:
            key = normalize_name(name)
            if not key:
                return
            existing = names.get(key)
            if existing:
                existing["current"] = existing.get("current", False) or current
                if existing.get("status") == "observed" and status in {"configured", "available"}:
                    existing["status"] = status
                return
            names[key] = {"name": name, "status": status, "source": source, "current": current}

        if settings_path.exists():
            try:
                settings = read_json(settings_path)
                if isinstance(settings, dict) and isinstance(settings.get("model"), str):
                    add(settings["model"], "configured", str(settings_path), True)
            except (OSError, ValueError) as exc:
                result["notes"].append(f"Could not parse Claude settings {settings_path}: {exc}")
        if state_path.exists() and include_observed:
            try:
                state = read_json(state_path)
                for name in walk_claude_models(state):
                    add(name, "observed", str(state_path))
            except (OSError, ValueError) as exc:
                result["notes"].append(f"Could not parse Claude state {state_path}: {exc}")

        claude_binary = shutil.which("claude")
        if claude_binary:
            try:
                help_text = subprocess.run(
                    [claude_binary, "--help"], capture_output=True, text=True, timeout=10, check=False
                ).stdout
                if "--model" in help_text:
                    for alias in ("opus", "sonnet", "haiku"):
                        add(alias, "cli-alias", f"{claude_binary} --help")
                    result["notes"].append(
                        "Claude Code exposes --model and the opus/sonnet/haiku aliases; "
                        "the CLI does not provide a complete public enumeration command"
                    )
            except (OSError, subprocess.SubprocessError) as exc:
                result["notes"].append(f"Could not inspect Claude CLI: {exc}")
        result["claude"] = list(names.values())

    return result


def all_runtime_names(runtime_data: dict[str, Any], runtime: str, include_observed: bool = True) -> list[str]:
    records = runtime_data.get(runtime, []) if runtime in {"codex", "claude"} else (
        runtime_data.get("codex", []) + runtime_data.get("claude", [])
    )
    allowed = {"available", "configured", "cli-alias"}
    if include_observed:
        allowed.add("observed")
    return [record["name"] for record in records if record.get("status") in allowed]


def clean_for_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: clean_for_json(child) for key, child in value.items()}
    if isinstance(value, list):
        return [clean_for_json(child) for child in value]
    return value


def text_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def table(rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> str:
    values = [[text_value(row.get(key)) for _, key in columns] for row in rows]
    widths = [len(label) for label, _ in columns]
    for index in range(len(columns)):
        widths[index] = min(42, max(widths[index], *(len(value) for value in (row[index] for row in values))))
    head = "  ".join(label.ljust(widths[index]) for index, (label, _) in enumerate(columns))
    line = "  ".join("-" * width for width in widths)
    body = ["  ".join(value[:42].ljust(widths[index]) for index, value in enumerate(row)) for row in values]
    return "\n".join([head, line, *body])


def markdown(rows: list[dict[str, Any]], columns: list[tuple[str, str]]) -> str:
    header = "| " + " | ".join(label for label, _ in columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(text_value(row.get(key)).replace("|", "\\|") for _, key in columns) + " |")
    return "\n".join([header, separator, *body])


def rank_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.available_only and not args.runtime:
        raise RuntimeError("--available-only requires --runtime codex, claude, or all")
    payload, _ = fetch_models(
        cache_dir=Path(args.cache_dir).expanduser() if args.cache_dir else None,
        credentials=Path(args.credentials).expanduser() if args.credentials else None,
        max_age=args.max_age,
        refresh=args.refresh,
        stale_if_error=not args.no_stale_if_error,
    )
    runtime_data = discover_runtime(args.runtime) if args.runtime else {"codex": [], "claude": []}
    names = all_runtime_names(runtime_data, args.runtime, include_observed=not args.available_only) if args.runtime else []
    rows = enrich_models(payload_data(payload), topic=args.topic, metric=args.metric, runtime_names=names)
    if args.available_only:
        rows = [row for row in rows if row["runtime_matches"]]
    if args.sort == "cost-per-intelligence":
        rows.sort(key=lambda row: row.get("cost_per_intelligence_point") is None)
        rows.sort(key=lambda row: row.get("cost_per_intelligence_point") or float("inf"))
    elif args.sort == "speed":
        rows.sort(key=lambda row: row.get("median_output_tokens_per_second") or -1, reverse=True)
    elif args.sort == "price":
        rows.sort(key=lambda row: row.get("blended_price_per_1m_tokens") or float("inf"))
    else:
        rows.sort(key=lambda row: row.get("selected_score") or -1, reverse=True)
    return rows[: args.limit] if args.limit else rows


def rank_command(args: argparse.Namespace) -> None:
    rows = rank_rows(args)
    if args.format == "json":
        print(json.dumps(clean_for_json(rows), indent=2, ensure_ascii=True))
        return
    if args.format == "csv":
        columns = [("name", "name"), ("score", "selected_score"), ("metric", "selected_metric"), ("blended_$", "blended_price_per_1m_tokens"), ("$/100_pts", "cost_per_100_intelligence_points"), ("out_tok/s", "median_output_tokens_per_second"), ("available_as", "runtime_matches")]
        writer = csv.writer(sys.stdout)
        writer.writerow([label for label, _ in columns])
        for row in rows:
            writer.writerow([row.get(key) for _, key in columns])
        return
    columns = [
        ("Model", "name"),
        ("Score", "selected_score"),
        ("Metric", "selected_metric"),
        ("Blend $/1M", "blended_price_per_1m_tokens"),
        ("$/100 pts", "cost_per_100_intelligence_points"),
        ("Out tok/s", "median_output_tokens_per_second"),
        ("Runtime match", "runtime_matches"),
    ]
    if args.metrics == "all":
        metric_keys = sorted({key for row in rows for key in row["evaluations"]})
        columns.extend((key, f"metric:{key}") for key in metric_keys)
        for row in rows:
            for _, key in columns:
                if key.startswith("metric:"):
                    row[key] = row["evaluations"].get(key[7:])
    elif args.metrics:
        for key in args.metrics.split(","):
            columns.append((key, f"metric:{key}"))
            for row in rows:
                found = matching_key(row["evaluations"], key)
                row[f"metric:{key}"] = row["evaluations"].get(found) if found else None
    print(markdown(rows, columns) if args.format == "markdown" else table(rows, columns))


def discover_command(args: argparse.Namespace) -> None:
    data = discover_runtime(args.runtime, include_observed=not args.no_observed)
    if args.format == "json":
        print(json.dumps(clean_for_json(data), indent=2, ensure_ascii=True))
        return
    rows = data.get(args.runtime, []) if args.runtime in {"codex", "claude"} else data.get("codex", []) + data.get("claude", [])
    columns = [("Runtime", "runtime"), ("Model", "name"), ("Status", "status"), ("Current", "current"), ("Source", "source")]
    for row in rows:
        row["runtime"] = args.runtime if args.runtime in {"codex", "claude"} else ("claude" if "claude" in row.get("source", "") else "codex")
    print(markdown(rows, columns) if args.format == "markdown" else table(rows, columns))
    for note in data.get("notes", []):
        print(f"note: {note}", file=sys.stderr)


def fetch_command(args: argparse.Namespace) -> None:
    payload, info = fetch_models(
        cache_dir=Path(args.cache_dir).expanduser() if args.cache_dir else None,
        credentials=Path(args.credentials).expanduser() if args.credentials else None,
        max_age=args.max_age,
        refresh=args.refresh,
        stale_if_error=not args.no_stale_if_error,
    )
    if args.format == "json":
        print(json.dumps(clean_for_json(payload), indent=2, ensure_ascii=True))
    else:
        print(f"{info['source']}: {info['path']} ({len(payload_data(payload))} models)")


def add_fetch_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--cache-dir", help="Cache directory; defaults to <skill>/.cache")
    parser.add_argument("--credentials", help="JSON credentials file; defaults to <skill>/creds.json")
    parser.add_argument("--max-age", type=float, default=DEFAULT_MAX_AGE, help="Use cache for this many seconds")
    parser.add_argument("--refresh", action="store_true", help="Force a network fetch")
    parser.add_argument("--no-stale-if-error", action="store_true", help="Fail instead of using stale cache on fetch errors")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser("fetch", help="Fetch or refresh the cached Artificial Analysis model catalog")
    add_fetch_options(fetch)
    fetch.add_argument("--format", choices=("summary", "json"), default="summary")
    fetch.set_defaults(function=fetch_command)

    discover = subparsers.add_parser("discover", help="Inspect models exposed by the local Codex or Claude Code runtime")
    discover.add_argument("--runtime", choices=("all", "codex", "claude"), default="all")
    discover.add_argument("--format", choices=("table", "markdown", "json"), default="table")
    discover.add_argument("--no-observed", action="store_true", help="Omit models only observed in local state")
    discover.set_defaults(function=discover_command)

    rank = subparsers.add_parser("rank", help="Rank the cached model catalog")
    add_fetch_options(rank)
    rank.add_argument("--topic", choices=sorted(TOPIC_ALIASES), default="general")
    rank.add_argument("--metric", help="Exact benchmark/field name; overrides --topic")
    rank.add_argument("--sort", choices=("score", "cost-per-intelligence", "speed", "price"), default="score")
    rank.add_argument("--runtime", choices=("all", "codex", "claude"), help="Attach local runtime matches")
    rank.add_argument("--available-only", action="store_true", help="Keep only models matching a local runtime discovery")
    rank.add_argument("--metrics", help="Comma-separated extra evaluation fields, or 'all'")
    rank.add_argument("--limit", type=int)
    rank.add_argument("--format", choices=("table", "markdown", "csv", "json"), default="table")
    rank.set_defaults(function=rank_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.function(args)
        return 0
    except (RuntimeError, OSError, urllib.error.URLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
