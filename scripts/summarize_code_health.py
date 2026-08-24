#!/usr/bin/env python3
"""Normalize compatible weighted code-health JSON without treating scores as verdicts."""

from __future__ import annotations

import argparse
import json
import math
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


MAX_REPORT_BYTES = 50 * 1024 * 1024
MAX_MARKDOWN_FIELD_CHARS = 500
TOOL_SEVERITY_ORDER = {"critical": 0, "error": 1, "warning": 2, "info": 3, "unavailable": 4}


class CodeHealthError(ValueError):
    """Raised for malformed or unsupported code-health input."""


def _reject_json_constant(value: str) -> None:
    raise CodeHealthError(f"non-standard JSON constant is not allowed: {value}")


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if math.isfinite(value) else None


def _count(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def load_report(path: Path) -> dict[str, Any]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise CodeHealthError(f"cannot read report metadata: {exc}") from exc

    if size > MAX_REPORT_BYTES:
        raise CodeHealthError(
            f"report is {size} bytes; the safe limit is {MAX_REPORT_BYTES} bytes"
        )

    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise CodeHealthError(f"cannot parse JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise CodeHealthError("code-health report root must be a JSON object")
    if "files" not in data or not isinstance(data["files"], list):
        raise CodeHealthError("code-health report must contain a files array")
    if "summary" not in data or not isinstance(data["summary"], dict):
        raise CodeHealthError("code-health report must contain a summary object")
    if "$schema" in data and not isinstance(data["$schema"], dict):
        raise CodeHealthError("code-health report $schema must be an object when present")
    if "aggregatedMetrics" in data:
        if not isinstance(data["aggregatedMetrics"], list):
            raise CodeHealthError("code-health report aggregatedMetrics must be an array")
        if any(not isinstance(metric, dict) for metric in data["aggregatedMetrics"]):
            raise CodeHealthError(
                "code-health report aggregatedMetrics entries must be objects"
            )
    for file_index, file_entry in enumerate(data["files"]):
        if not isinstance(file_entry, dict):
            raise CodeHealthError(
                f"code-health report files[{file_index}] must be an object"
            )
        if not isinstance(file_entry.get("metrics"), list):
            raise CodeHealthError(
                f"code-health report files[{file_index}].metrics must be an array"
            )
        if not isinstance(file_entry.get("parseResult"), dict):
            raise CodeHealthError(
                f"code-health report files[{file_index}].parseResult must be an object"
            )
        for metric_index, metric in enumerate(file_entry["metrics"]):
            if not isinstance(metric, dict):
                raise CodeHealthError(
                    f"code-health report files[{file_index}].metrics[{metric_index}] "
                    "must be an object"
                )
            if "locations" in metric:
                if not isinstance(metric["locations"], list):
                    raise CodeHealthError(
                        f"code-health report files[{file_index}].metrics[{metric_index}]"
                        ".locations must be an array"
                    )
                if any(not isinstance(location, dict) for location in metric["locations"]):
                    raise CodeHealthError(
                        f"code-health report files[{file_index}].metrics[{metric_index}]"
                        ".locations entries must be objects"
                    )
    return data


def _normalize_location(raw_location: Any) -> dict[str, Any] | None:
    location = _mapping(raw_location)
    if not location:
        return None
    line = _count(location.get("line"))
    column = _count(location.get("column"))
    return {
        "path": _text(location.get("filePath")) or _text(location.get("path")),
        "line": line,
        "column": column,
        "function": _text(location.get("functionName")) or _text(location.get("symbol")),
        "message": _text(location.get("message")),
    }


def _normalize_metric(raw_metric: Any) -> dict[str, Any]:
    metric = _mapping(raw_metric)
    locations = [
        normalized
        for raw_location in _list(metric.get("locations"))
        if (normalized := _normalize_location(raw_location)) is not None
    ]
    severity = _text(metric.get("severity"), "unavailable").lower()
    if severity not in TOOL_SEVERITY_ORDER:
        severity = "unavailable"
    return {
        "name": _text(metric.get("name"), "(unknown-metric)"),
        "category": _text(metric.get("category"), "unavailable"),
        "value": _number(metric.get("value")),
        "normalized_score": _number(metric.get("normalizedScore")),
        "tool_severity": severity,
        "details": _text(metric.get("details")),
        "locations": locations,
        "location_field_present": "locations" in metric,
    }


def _normalize_file(raw_file: Any, input_index: int) -> dict[str, Any]:
    file_entry = _mapping(raw_file)
    parse_result = _mapping(file_entry.get("parseResult"))
    metrics = [_normalize_metric(raw) for raw in _list(file_entry.get("metrics"))]
    return {
        "input_index": input_index,
        "path": _text(file_entry.get("path"), "(unknown-file)"),
        "tool_score": _number(file_entry.get("score")),
        "language": _text(parse_result.get("language"), "unavailable"),
        "total_lines": _count(parse_result.get("totalLines")),
        "code_lines": _count(parse_result.get("codeLines")),
        "comment_lines": _count(parse_result.get("commentLines")),
        "function_count": _count(parse_result.get("functionCount")),
        "class_count": _count(parse_result.get("classCount")),
        "metrics": sorted(
            metrics,
            key=lambda item: (
                TOOL_SEVERITY_ORDER[item["tool_severity"]],
                item["name"],
            ),
        ),
    }


def _coverage_state(
    total_files: int | None,
    analyzed_files: int | None,
    skipped_files: int | None,
    reported_file_count: int,
) -> tuple[str, int | None, list[str]]:
    notices: list[str] = []
    if total_files is None or analyzed_files is None or skipped_files is None:
        notices.append("Coverage counts are missing or invalid; report completeness is unknown.")
        return "unknown", None, notices

    if (
        analyzed_files > total_files
        or skipped_files > total_files
        or analyzed_files + skipped_files > total_files
        or reported_file_count > analyzed_files
    ):
        notices.append("Coverage counts are internally inconsistent.")
        return "unknown", None, notices

    eligible_files = total_files - skipped_files
    unresolved_files = max(0, eligible_files - analyzed_files)

    if reported_file_count != analyzed_files:
        notices.append(
            "The files array length does not match summary.analyzedFiles; "
            "per-file coverage is incomplete."
        )

    if total_files == 0 and analyzed_files == 0:
        notices.append("No files were in the reported scan scope.")
        return "empty_scope", 0, notices

    if analyzed_files == 0:
        notices.append(
            "No files were analyzed; any reported overall score is not evidence of healthy code."
        )
        return "not_populated", unresolved_files, notices

    if skipped_files > 0 or unresolved_files > 0 or reported_file_count != analyzed_files:
        notices.append(
            "Only part of the discovered scope was analyzed; skipped and unresolved files "
            "must remain visible."
        )
        return "partial", unresolved_files, notices

    return "available", 0, notices


def normalize_report(
    data: dict[str, Any], source: str = "", tool_name: str = ""
) -> dict[str, Any]:
    summary = _mapping(data.get("summary"))
    schema = _mapping(data.get("$schema"))
    total_files = _count(summary.get("totalFiles"))
    analyzed_files = _count(summary.get("analyzedFiles"))
    skipped_files = _count(summary.get("skippedFiles"))
    raw_files = _list(data.get("files"))
    files = [_normalize_file(raw, index) for index, raw in enumerate(raw_files)]
    files.sort(
        key=lambda item: (
            item["tool_score"] is None,
            item["tool_score"] if item["tool_score"] is not None else 0,
            item["path"],
        )
    )

    coverage_state, unresolved_files, notices = _coverage_state(
        total_files, analyzed_files, skipped_files, len(files)
    )
    tool_overall_score = _number(data.get("overallScore"))
    if tool_overall_score is not None and not 0 <= tool_overall_score <= 100:
        notices.append("The reported overall score is outside the documented 0-100 scale.")

    config_fields = [
        key for key in ("configuration", "config", "invocation") if isinstance(data.get(key), dict)
    ]
    configuration_state = "available" if config_fields else "unavailable"
    if configuration_state == "unavailable":
        notices.append(
            "Analyzer configuration, metric weights, include patterns, and exclusions are not "
            "present in this report; do not compare or gate on its score without them."
        )

    metrics = [metric for file_entry in files for metric in file_entry["metrics"]]
    aggregated_metrics = []
    for raw_metric in _list(data.get("aggregatedMetrics")):
        metric = _mapping(raw_metric)
        aggregated_metrics.append(
            {
                "name": _text(metric.get("name"), "(unknown-metric)"),
                "category": _text(metric.get("category"), "unavailable"),
                "average": _number(metric.get("average")),
                "min": _number(metric.get("min")),
                "max": _number(metric.get("max")),
                "median": _number(metric.get("median")),
            }
        )
    metrics_with_location_field = sum(metric["location_field_present"] for metric in metrics)
    metrics_with_locations = sum(bool(metric["locations"]) for metric in metrics)
    if not metrics or metrics_with_location_field == 0:
        location_metadata_state = "absent"
        notices.append(
            "Metric locations are absent; exact line or symbol claims require direct source inspection."
        )
    elif metrics_with_locations == len(metrics):
        location_metadata_state = "available"
    else:
        location_metadata_state = "partial"
        notices.append(
            "Metric location metadata is partial; do not generalize exact locations to every signal."
        )

    notices.insert(
        0,
        "Normalization only: tool scores and severities remain unverified signals, not findings.",
    )

    return {
        "source": source,
        "format_profile": "weighted-code-health-json",
        "tool_name": tool_name or "unattributed",
        "reported_version": _text(schema.get("version"), "unavailable"),
        "project_path": _text(data.get("projectPath"), "unavailable"),
        "coverage_state": coverage_state,
        "total_files": total_files,
        "analyzed_files": analyzed_files,
        "reported_file_count": len(files),
        "skipped_files": skipped_files,
        "unresolved_files": unresolved_files,
        "analysis_time_ms": _number(summary.get("analysisTime")),
        "tool_overall_score": tool_overall_score,
        "configuration_state": configuration_state,
        "configuration_fields": config_fields,
        "location_metadata_state": location_metadata_state,
        "language_counts": dict(Counter(item["language"] for item in files)),
        "tool_severity_counts": dict(
            Counter(metric["tool_severity"] for metric in metrics)
        ),
        "aggregated_metrics": aggregated_metrics,
        "files": files,
        "notices": notices,
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


def _format_number(value: int | float | None) -> str:
    if value is None:
        return "unavailable"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return f"{value:.2f}" if isinstance(value, float) else str(value)


def render_markdown(summary: dict[str, Any], limit: int) -> str:
    lines = [
        "# Code Health Report Normalization",
        "",
        f"> {_escape_markdown(summary['notices'][0])}",
        "",
        f"- Source: `{_escape_markdown(summary['source'] or '(in-memory)')}`",
        f"- Tool attribution: `{_escape_markdown(summary['tool_name'])}`",
        f"- Reported version: `{_escape_markdown(summary['reported_version'])}`",
        f"- Reported project path: `{_escape_markdown(summary['project_path'])}`",
        f"- Coverage state: `{_escape_markdown(summary['coverage_state'])}`",
        f"- Total / analyzed / skipped / unresolved files: "
        f"{_format_number(summary['total_files'])} / "
        f"{_format_number(summary['analyzed_files'])} / "
        f"{_format_number(summary['skipped_files'])} / "
        f"{_format_number(summary['unresolved_files'])}",
        f"- Tool overall score: `{_format_number(summary['tool_overall_score'])}`",
        f"- Configuration metadata: `{_escape_markdown(summary['configuration_state'])}`",
        f"- Metric location metadata: `{_escape_markdown(summary['location_metadata_state'])}`",
        "",
        "## Completeness Notices",
        "",
    ]
    for notice in summary["notices"][1:]:
        lines.append(f"- {_escape_markdown(notice)}")

    lines.extend(
        [
            "",
            "## File Signals",
            "",
            "| File | Tool score | Language | Highest tool severity | Metrics |",
            "|---|---:|---|---|---:|",
        ]
    )
    files = summary["files"] if limit == 0 else summary["files"][:limit]
    for file_entry in files:
        severities = [
            metric["tool_severity"] for metric in file_entry["metrics"]
        ]
        highest_severity = min(
            severities,
            key=lambda severity: TOOL_SEVERITY_ORDER[severity],
            default="unavailable",
        )
        lines.append(
            "| {path} | {score} | {language} | {severity} | {count} |".format(
                path=_escape_markdown(file_entry["path"]),
                score=_format_number(file_entry["tool_score"]),
                language=_escape_markdown(file_entry["language"]),
                severity=_escape_markdown(highest_severity),
                count=len(file_entry["metrics"]),
            )
        )

    omitted = len(summary["files"]) - len(files)
    if omitted > 0:
        lines.extend(["", f"{omitted} file signal(s) omitted by `--limit`."])

    lines.extend(
        [
            "",
            "## Metric Signals",
            "",
            "| File | Metric | Category | Tool severity | Value | Normalized score | Location | Details |",
            "|---|---|---|---|---:|---:|---|---|",
        ]
    )
    for file_entry in files:
        for metric in file_entry["metrics"]:
            if metric["locations"]:
                first_location = metric["locations"][0]
                location = first_location["path"] or file_entry["path"]
                if first_location["line"] is not None:
                    location = f"{location}:{first_location['line']}"
                if len(metric["locations"]) > 1:
                    location = f"{location} (+{len(metric['locations']) - 1} more)"
            else:
                location = "unavailable"
            lines.append(
                "| {path} | {metric} | {category} | {severity} | {value} | {score} | {location} | {details} |".format(
                    path=_escape_markdown(file_entry["path"]),
                    metric=_escape_markdown(metric["name"]),
                    category=_escape_markdown(metric["category"]),
                    severity=_escape_markdown(metric["tool_severity"]),
                    value=_format_number(metric["value"]),
                    score=_format_number(metric["normalized_score"]),
                    location=_escape_markdown(location),
                    details=_escape_markdown(metric["details"]),
                )
            )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize compatible weighted code-health JSON without validating findings."
    )
    parser.add_argument("report", type=Path, help="Path to a code-health JSON report")
    parser.add_argument(
        "--tool-name",
        default="",
        help="Explicit tool attribution; reports without it remain unattributed",
    )
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown", help="Output format"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum file signals in Markdown; 0 means all (default: 100)",
    )
    args = parser.parse_args(argv)
    if args.limit < 0:
        parser.error("--limit must be 0 or greater")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        data = load_report(args.report)
        summary = normalize_report(data, str(args.report), args.tool_name)
    except CodeHealthError as exc:
        print(f"error: {_sanitize_controls(exc)}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(render_markdown(summary, args.limit), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
