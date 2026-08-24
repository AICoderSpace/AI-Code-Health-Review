#!/usr/bin/env python3
"""Normalize SARIF 2.1.0 metadata without asserting that findings are valid."""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


MAX_REPORT_BYTES = 50 * 1024 * 1024
MAX_MARKDOWN_FIELD_CHARS = 500
BASELINE_ORDER = {"new": 0, "updated": 1, "unchanged": 2, "unavailable": 3, "absent": 4}
LEVEL_ORDER = {"error": 0, "warning": 1, "note": 2, "none": 3, "unavailable": 4}


class SarifError(ValueError):
    """Raised for malformed or unsupported SARIF input."""


def _reject_json_constant(value: str) -> None:
    raise SarifError(f"non-standard JSON constant is not allowed: {value}")


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def load_sarif(path: Path) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise SarifError(f"cannot read report metadata: {exc}") from exc

    if size > MAX_REPORT_BYTES:
        raise SarifError(
            f"report is {size} bytes; the safe limit is {MAX_REPORT_BYTES} bytes"
        )

    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise SarifError(f"cannot parse JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise SarifError("SARIF root must be a JSON object")
    if data.get("version") != "2.1.0":
        raise SarifError("only SARIF version 2.1.0 is supported")
    if "runs" not in data:
        raise SarifError("SARIF root must contain a runs property")
    if data["runs"] is not None and not isinstance(data["runs"], list):
        raise SarifError("SARIF runs property must be null or an array")
    return data


def _driver(run: dict[str, Any]) -> dict[str, Any]:
    return _mapping(_mapping(run.get("tool")).get("driver"))


def _valid_index(value: Any, length: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value < length


def _component_for_result(
    result: dict[str, Any], driver: dict[str, Any], extensions: list[Any]
) -> tuple[dict[str, Any], str, str, int | None]:
    rule_reference = _mapping(result.get("rule"))
    component_reference = _mapping(rule_reference.get("toolComponent"))
    if component_reference:
        component_index = component_reference.get("index")
        if _valid_index(component_index, len(extensions)):
            component = _mapping(extensions[component_index])
            name = _text(component.get("name"), f"extension[{component_index}]")
            return component, name, "extension", component_index

        reference_guid = _text(component_reference.get("guid"))
        for index, raw_component in enumerate(extensions):
            component = _mapping(raw_component)
            if reference_guid and _text(component.get("guid")) == reference_guid:
                return component, _text(component.get("name"), reference_guid), "extension", index

    return driver, _text(driver.get("name"), "(unknown-tool)"), "driver", None


def _rule_for_result(
    result: dict[str, Any], component: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    rule_reference = _mapping(result.get("rule"))
    rule_id = _text(result.get("ruleId")) or _text(rule_reference.get("id"))
    rule_index = result.get("ruleIndex")
    if not _valid_index(rule_index, len(_list(component.get("rules")))):
        rule_index = rule_reference.get("index")
    rules = _list(component.get("rules"))
    rule: dict[str, Any] = {}

    if _valid_index(rule_index, len(rules)):
        indexed_rule = _mapping(rules[rule_index])
        if not rule_id or _text(indexed_rule.get("id")) == rule_id:
            rule = indexed_rule
    if not rule and rule_id:
        for candidate in rules:
            candidate_rule = _mapping(candidate)
            if _text(candidate_rule.get("id")) == rule_id:
                rule = candidate_rule
                break

    if not rule_id:
        rule_id = _text(rule.get("id"), "(unknown-rule)")
    return rule_id, rule


def _descriptor_text(descriptor: dict[str, Any], key: str) -> str:
    value = _mapping(descriptor.get(key))
    return _text(value.get("text")) or _text(value.get("markdown")) or _text(value.get("id"))


def _rule_name(rule: dict[str, Any]) -> str:
    return (
        _text(rule.get("name"))
        or _descriptor_text(rule, "shortDescription")
        or "unavailable"
    )


def _rank(result: dict[str, Any], rule: dict[str, Any]) -> int | float | None:
    value = result.get("rank")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        value = _mapping(rule.get("defaultConfiguration")).get("rank")
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _message(result: dict[str, Any]) -> str:
    message = _mapping(result.get("message"))
    return (
        _text(message.get("text"))
        or _text(message.get("markdown"))
        or _text(message.get("id"))
        or "(no message)"
    )


def _locations(result: dict[str, Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for raw_location in _list(result.get("locations")):
        location = _mapping(raw_location)
        physical = _mapping(location.get("physicalLocation"))
        artifact = _mapping(physical.get("artifactLocation"))
        region = _mapping(physical.get("region"))
        line_value = region.get("startLine")
        line = (
            line_value
            if isinstance(line_value, int)
            and not isinstance(line_value, bool)
            and line_value > 0
            else None
        )

        logical_name = ""
        logical_locations = _list(location.get("logicalLocations"))
        if logical_locations:
            logical = _mapping(logical_locations[0])
            logical_name = _text(logical.get("fullyQualifiedName")) or _text(
                logical.get("name")
            )
        normalized.append(
            {
                "uri": _text(artifact.get("uri"), "(unknown)"),
                "uri_base_id": _text(artifact.get("uriBaseId")),
                "line": line,
                "logical_name": logical_name,
            }
        )
    return normalized or [
        {"uri": "(unknown)", "uri_base_id": "", "line": None, "logical_name": ""}
    ]


def _fingerprints(result: dict[str, Any]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for container_name in ("partialFingerprints", "fingerprints"):
        container = _mapping(result.get(container_name))
        for key, value in container.items():
            if isinstance(key, str) and isinstance(value, str):
                pairs.append((f"{container_name}.{key}", value))
    return sorted(pairs)


def _suppression(
    result: dict[str, Any],
) -> tuple[str, bool, list[dict[str, str]]]:
    raw_suppressions = result.get("suppressions")
    if "suppressions" not in result or raw_suppressions is None:
        return "unavailable", False, []
    if not isinstance(raw_suppressions, list):
        return "unavailable", False, []
    suppressions = raw_suppressions
    if not suppressions:
        return "not suppressed", False, []

    labels: list[str] = []
    normalized: list[dict[str, str]] = []
    for item in suppressions:
        suppression = _mapping(item)
        kind = _text(suppression.get("kind"), "suppressed")
        status = _text(suppression.get("status"))
        justification = _text(suppression.get("justification"))
        labels.append(f"{kind}:{status}" if status else kind)
        normalized.append(
            {"kind": kind, "status": status, "justification": justification}
        )
    is_suppressed = any(item["status"] in {"", "accepted"} for item in normalized)
    return ", ".join(labels), is_suppressed, normalized


def _tool_version(driver: dict[str, Any]) -> str:
    return (
        _text(driver.get("semanticVersion"))
        or _text(driver.get("version"))
        or _text(driver.get("dottedQuadFileVersion"))
        or "unavailable"
    )


def normalize_sarif(data: dict[str, Any], source: str = "") -> dict[str, Any]:
    normalized_runs: list[dict[str, Any]] = []
    normalized_results: list[dict[str, Any]] = []
    seen: dict[tuple[Any, ...], int] = {}
    duplicates_collapsed = 0
    raw_runs = data.get("runs")
    if "runs" not in data:
        runs_state = "missing"
    elif raw_runs is None:
        runs_state = "population_failed"
    elif isinstance(raw_runs, list):
        runs_state = "available" if raw_runs else "empty"
    else:
        runs_state = "invalid"

    for run_index, raw_run in enumerate(_list(raw_runs)):
        run = _mapping(raw_run)
        driver = _driver(run)
        tool_name = _text(driver.get("name"), "(unknown-tool)")
        tool_version = _tool_version(driver)
        extensions = _list(_mapping(run.get("tool")).get("extensions"))
        raw_results = _list(run.get("results"))

        normalized_runs.append(
            {
                "run": run_index + 1,
                "tool": tool_name,
                "version": tool_version,
                "result_count": len(raw_results),
                "automation_id": _text(
                    _mapping(run.get("automationDetails")).get("id"), "unavailable"
                ),
                "baseline_guid": _text(run.get("baselineGuid"), "unavailable"),
            }
        )

        for result_index, raw_result in enumerate(raw_results):
            result = _mapping(raw_result)
            component, component_name, component_kind, component_index = (
                _component_for_result(result, driver, extensions)
            )
            rule_id, rule = _rule_for_result(result, component)
            level = _text(result.get("level")) or _text(
                _mapping(rule.get("defaultConfiguration")).get("level"), "unavailable"
            )
            baseline = _text(result.get("baselineState"), "unavailable")
            message = _message(result)
            locations = _locations(result)
            primary_location = locations[0]
            uri = primary_location["uri"]
            line = primary_location["line"]
            logical_name = primary_location["logical_name"]
            fingerprints = _fingerprints(result)
            suppression, is_suppressed, suppressions = _suppression(result)
            help_uri = (
                _text(rule.get("helpUri"))
                or _text(component.get("informationUri"))
                or _text(driver.get("informationUri"))
            )
            code_flow_count = len(_list(result.get("codeFlows")))
            component_identity = (
                component_kind,
                component_index,
                component_name,
                _text(component.get("guid")),
            )

            if fingerprints:
                identity: tuple[Any, ...] = (
                    run_index,
                    tool_name,
                    component_identity,
                    rule_id,
                    tuple(fingerprints),
                )
                identity_source = "supplied fingerprint"
            else:
                identity = (
                    run_index,
                    tool_name,
                    component_identity,
                    rule_id,
                    tuple(
                        (
                            location["uri"],
                            location["uri_base_id"],
                            location["line"],
                            location["logical_name"],
                        )
                        for location in locations
                    ),
                    message,
                )
                identity_source = "heuristic location/message"

            if identity in seen:
                existing = normalized_results[seen[identity]]
                existing["duplicate_count"] += 1
                if LEVEL_ORDER.get(level, 5) < LEVEL_ORDER.get(existing["level"], 5):
                    existing["level"] = level
                if BASELINE_ORDER.get(baseline, 5) < BASELINE_ORDER.get(
                    existing["baseline_state"], 5
                ):
                    existing["baseline_state"] = baseline
                if suppression not in existing["suppression_states"]:
                    existing["suppression_states"].append(suppression)
                for item in suppressions:
                    if item not in existing["suppressions"]:
                        existing["suppressions"].append(item)
                for location in locations:
                    if location not in existing["locations"]:
                        existing["locations"].append(location)
                existing["is_suppressed"] = existing["is_suppressed"] and is_suppressed
                existing["code_flow_count"] = max(
                    existing["code_flow_count"], code_flow_count
                )
                incoming_rank = _rank(result, rule)
                if incoming_rank is not None and (
                    existing["rank"] is None or incoming_rank > existing["rank"]
                ):
                    existing["rank"] = incoming_rank
                duplicates_collapsed += 1
                continue

            item = {
                "run": run_index + 1,
                "result": result_index + 1,
                "tool": tool_name,
                "tool_version": tool_version,
                "rule_component": component_name,
                "rule_component_kind": component_kind,
                "rule_component_index": component_index,
                "rule_id": rule_id,
                "rule_name": _rule_name(rule),
                "level": level,
                "rank": _rank(result, rule),
                "baseline_state": baseline,
                "uri": uri,
                "line": line,
                "logical_name": logical_name,
                "locations": locations,
                "message": message,
                "help_uri": help_uri,
                "fingerprints": [f"{key}={value}" for key, value in fingerprints],
                "identity_source": identity_source,
                "suppression": suppression,
                "suppressions": suppressions,
                "suppression_states": [suppression],
                "is_suppressed": is_suppressed,
                "code_flow_count": code_flow_count,
                "duplicate_count": 1,
                "verification_status": "unverified",
            }
            seen[identity] = len(normalized_results)
            normalized_results.append(item)

    for item in normalized_results:
        states = item.pop("suppression_states")
        if len(states) > 1:
            item["suppression"] = "mixed: " + "; ".join(states)

    normalized_results.sort(
        key=lambda item: (
            BASELINE_ORDER.get(item["baseline_state"], 5),
            LEVEL_ORDER.get(item["level"], 5),
            item["is_suppressed"],
            item["rule_component"],
            item["uri"],
            item["line"] if item["line"] is not None else -1,
            item["rule_id"],
        )
    )

    notice = (
        "Normalization only. Source behavior, reachability, exploitability, severity, "
        "and correctness remain unverified. Output retains report paths and messages, "
        "which may be sensitive."
    )
    if runs_state == "population_failed":
        notice = (
            "SARIF runs is null: the producer attempted to populate runs but failed; "
            "result-set completeness is unknown. "
            + notice
        )

    return {
        "source": source,
        "sarif_version": data.get("version"),
        "runs_state": runs_state,
        "runs": normalized_runs,
        "raw_result_count": sum(run["result_count"] for run in normalized_runs),
        "normalized_result_count": len(normalized_results),
        "duplicates_collapsed": duplicates_collapsed,
        "baseline_counts": dict(Counter(item["baseline_state"] for item in normalized_results)),
        "level_counts": dict(Counter(item["level"] for item in normalized_results)),
        "suppression_metadata_count": sum(
            bool(item["suppressions"]) for item in normalized_results
        ),
        "suppressed_count": sum(item["is_suppressed"] for item in normalized_results),
        "results": normalized_results,
        "notice": notice,
    }


def _escape_control_character(character: str) -> str:
    codepoint = ord(character)
    if codepoint <= 0xFF:
        return f"\\x{codepoint:02x}"
    if codepoint <= 0xFFFF:
        return f"\\u{codepoint:04x}"
    return f"\\U{codepoint:08x}"


def _sanitize_controls(value: Any) -> str:
    raw = str(value).replace("\n", " ").replace("\r", " ")
    return "".join(
        _escape_control_character(character)
        if unicodedata.category(character).startswith("C")
        else character
        for character in raw
    )


def _escape_markdown(value: Any) -> str:
    sanitized = _sanitize_controls(value)
    if len(sanitized) > MAX_MARKDOWN_FIELD_CHARS:
        sanitized = sanitized[: MAX_MARKDOWN_FIELD_CHARS - 3] + "..."
    for character in ("\\", "|", "`", "*", "_", "[", "]", "<", ">"):
        sanitized = sanitized.replace(character, f"\\{character}")
    return sanitized


def render_markdown(summary: dict[str, Any], limit: int) -> str:
    lines = [
        "# SARIF Normalization Summary",
        "",
        f"> {_escape_markdown(summary['notice'])}",
        "",
        f"- Source: `{_escape_markdown(summary['source'] or '(in-memory)')}`",
        f"- SARIF version: `{summary['sarif_version']}`",
        f"- Runs state: `{_escape_markdown(summary['runs_state'])}`",
        f"- Runs: {len(summary['runs'])}",
        f"- Raw results: {summary['raw_result_count']}",
        f"- Normalized results: {summary['normalized_result_count']}",
        f"- Duplicates collapsed: {summary['duplicates_collapsed']}",
        f"- Results with suppression metadata: {summary['suppression_metadata_count']}",
        f"- Actively suppressed results: {summary['suppressed_count']}",
        "",
        "## Runs",
        "",
        "| Run | Tool | Version | Results | Automation ID | Baseline GUID |",
        "|---:|---|---|---:|---|---|",
    ]

    for run in summary["runs"]:
        lines.append(
            "| {run} | {tool} | {version} | {count} | {automation} | {baseline} |".format(
                run=run["run"],
                tool=_escape_markdown(run["tool"]),
                version=_escape_markdown(run["version"]),
                count=run["result_count"],
                automation=_escape_markdown(run["automation_id"]),
                baseline=_escape_markdown(run["baseline_guid"]),
            )
        )

    lines.extend(
        [
            "",
            "## Results",
            "",
            "| Tool/Rule | Level | Baseline | Location | Suppression | Identity | Message |",
            "|---|---|---|---|---|---|---|",
        ]
    )

    results = summary["results"] if limit == 0 else summary["results"][:limit]
    for item in results:
        location = item["uri"]
        if item["line"] is not None:
            location = f"{location}:{item['line']}"
        if len(item["locations"]) > 1:
            location = f"{location} (+{len(item['locations']) - 1} more)"
        tool_rule = f"{item['tool']}/{item['rule_id']}"
        if item["rule_component_kind"] == "extension":
            tool_rule = f"{item['tool']}[{item['rule_component']}]/{item['rule_id']}"
        duplicate_suffix = (
            f" (x{item['duplicate_count']})" if item["duplicate_count"] > 1 else ""
        )
        lines.append(
            "| {tool_rule} | {level} | {baseline} | {location} | {suppression} | {identity} | {message}{duplicates} |".format(
                tool_rule=_escape_markdown(tool_rule),
                level=_escape_markdown(item["level"]),
                baseline=_escape_markdown(item["baseline_state"]),
                location=_escape_markdown(location),
                suppression=_escape_markdown(item["suppression"]),
                identity=_escape_markdown(item["identity_source"]),
                message=_escape_markdown(item["message"]),
                duplicates=duplicate_suffix,
            )
        )

    omitted = summary["normalized_result_count"] - len(results)
    if omitted > 0:
        lines.extend(["", f"{omitted} normalized result(s) omitted by `--limit`."])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize SARIF 2.1.0 metadata without validating findings."
    )
    parser.add_argument("report", type=Path, help="Path to a SARIF 2.1.0 JSON file")
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown", help="Output format"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum normalized results in Markdown; 0 means all (default: 100)",
    )
    args = parser.parse_args(argv)
    if args.limit < 0:
        parser.error("--limit must be 0 or greater")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        data = load_sarif(args.report)
        summary = normalize_sarif(data, str(args.report))
    except SarifError as exc:
        print(f"error: {_sanitize_controls(exc)}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(render_markdown(summary, args.limit), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
