from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "summarize_code_health.py"
SPEC = importlib.util.spec_from_file_location("summarize_code_health", MODULE_PATH)
assert SPEC and SPEC.loader
health = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(health)


def sample_report() -> dict:
    return json.loads(
        (ROOT / "tests" / "fixtures" / "code-health.json").read_text(encoding="utf-8")
    )


class NormalizeCodeHealthTests(unittest.TestCase):
    def test_preserves_tool_signals_without_promoting_them_to_findings(self) -> None:
        summary = health.normalize_report(
            sample_report(), "report.json", "synthetic-analyzer"
        )

        self.assertEqual(summary["tool_name"], "synthetic-analyzer")
        self.assertEqual(summary["reported_version"], "synthetic-1.0")
        self.assertEqual(summary["tool_overall_score"], 72.5)
        self.assertEqual(summary["coverage_state"], "partial")
        self.assertEqual(summary["files"][0]["path"], "src/risky.py")
        self.assertEqual(summary["files"][0]["metrics"][0]["tool_severity"], "error")
        self.assertEqual(summary["aggregated_metrics"][0]["median"], 62)
        self.assertIn("unverified signals", summary["notices"][0])
        self.assertIn(
            "/synthetic/project",
            health.render_markdown(summary, limit=100),
        )

    def test_score_of_100_with_no_analyzed_files_is_not_healthy(self) -> None:
        data = sample_report()
        data["overallScore"] = 100
        data["summary"] = {
            "totalFiles": 4,
            "analyzedFiles": 0,
            "skippedFiles": 4,
            "analysisTime": 1,
        }
        data["files"] = []

        summary = health.normalize_report(data)

        self.assertEqual(summary["coverage_state"], "not_populated")
        self.assertTrue(
            any("not evidence of healthy code" in notice for notice in summary["notices"])
        )

    def test_detects_unresolved_analysis_failures(self) -> None:
        data = sample_report()
        data["summary"] = {
            "totalFiles": 5,
            "analyzedFiles": 2,
            "skippedFiles": 1,
            "analysisTime": 1,
        }

        summary = health.normalize_report(data)

        self.assertEqual(summary["coverage_state"], "partial")
        self.assertEqual(summary["unresolved_files"], 2)

    def test_rejects_internally_inconsistent_coverage_as_unknown(self) -> None:
        data = sample_report()
        data["summary"] = {
            "totalFiles": 2,
            "analyzedFiles": 2,
            "skippedFiles": 1,
            "analysisTime": 1,
        }

        summary = health.normalize_report(data)

        self.assertEqual(summary["coverage_state"], "unknown")
        self.assertIsNone(summary["unresolved_files"])
        self.assertTrue(
            any("internally inconsistent" in notice for notice in summary["notices"])
        )

    def test_marks_configuration_and_locations_unavailable_when_report_omits_them(self) -> None:
        summary = health.normalize_report(sample_report())

        self.assertEqual(summary["configuration_state"], "unavailable")
        self.assertEqual(summary["location_metadata_state"], "absent")

    def test_configuration_presence_is_recorded_without_copying_values(self) -> None:
        data = sample_report()
        data["config"] = {
            "exclude": ["generated/**"],
            "ai": {"apiKey": "synthetic-secret-must-not-escape"},
        }

        summary = health.normalize_report(data)
        rendered = json.dumps(summary)

        self.assertEqual(summary["configuration_state"], "available")
        self.assertEqual(summary["configuration_fields"], ["config"])
        self.assertNotIn("synthetic-secret-must-not-escape", rendered)

    def test_preserves_future_location_metadata_without_assuming_it_exists_everywhere(self) -> None:
        data = sample_report()
        data["files"][0]["metrics"][0]["locations"] = [
            {
                "filePath": "src/risky.py",
                "line": 42,
                "functionName": "process",
                "message": "branch hotspot",
            }
        ]

        summary = health.normalize_report(data)

        metric = summary["files"][0]["metrics"][0]
        self.assertEqual(metric["locations"][0]["line"], 42)
        self.assertEqual(summary["location_metadata_state"], "available")

    def test_markdown_escapes_untrusted_control_and_link_markup(self) -> None:
        data = sample_report()
        data["files"][0]["path"] = "\x1b\u202e[click](https://example.invalid)|`code`"

        rendered = health.render_markdown(health.normalize_report(data), limit=100)

        self.assertNotIn("\x1b", rendered)
        self.assertNotIn("\u202e", rendered)
        self.assertIn(r"\\x1b\\u202e\[click\](https://example.invalid)\|\`code\`", rendered)
        self.assertIn("cyclomatic\\_complexity", rendered)

    def test_load_rejects_nonstandard_json_constants(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text('{"summary":{},"files":[],"score":NaN}', encoding="utf-8")

            with self.assertRaises(health.CodeHealthError):
                health.load_report(path)

    def test_load_requires_files_and_summary_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text('{"files":[]}', encoding="utf-8")

            with self.assertRaises(health.CodeHealthError):
                health.load_report(path)

    def test_load_rejects_non_object_file_entries(self) -> None:
        data = sample_report()
        data["files"] = [None]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(health.CodeHealthError, r"files\[0\]"):
                health.load_report(path)

    def test_load_rejects_malformed_metric_locations(self) -> None:
        data = sample_report()
        data["files"][0]["metrics"][0]["locations"] = {"line": 1}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(health.CodeHealthError, "locations must be an array"):
                health.load_report(path)


if __name__ == "__main__":
    unittest.main()
