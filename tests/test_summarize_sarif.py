from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "summarize_sarif.py"
SPEC = importlib.util.spec_from_file_location("summarize_sarif", MODULE_PATH)
assert SPEC and SPEC.loader
sarif = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sarif)


def sample_sarif() -> dict:
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "ExampleScanner",
                        "semanticVersion": "1.2.3",
                        "rules": [
                            {
                                "id": "EX001",
                                "helpUri": "https://example.invalid/EX001",
                                "defaultConfiguration": {"level": "warning"},
                            }
                        ],
                    }
                },
                "automationDetails": {"id": "ci/main"},
                "baselineGuid": "baseline-guid",
                "results": [
                    {
                        "ruleIndex": 0,
                        "baselineState": "new",
                        "message": {"text": "Untrusted data reaches a sink"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "src/app.py"},
                                    "region": {"startLine": 12},
                                },
                                "logicalLocations": [{"fullyQualifiedName": "app.handle"}],
                            }
                        ],
                        "partialFingerprints": {"primaryLocationLineHash/v1": "abc123"},
                        "codeFlows": [{"threadFlows": []}],
                    },
                    {
                        "ruleId": "EX001",
                        "level": "error",
                        "baselineState": "new",
                        "message": {"text": "Duplicate representation"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "src/app.py"},
                                    "region": {"startLine": 99},
                                }
                            }
                        ],
                        "partialFingerprints": {"primaryLocationLineHash/v1": "abc123"},
                    },
                    {
                        "ruleId": "EX002",
                        "level": "note",
                        "message": {"text": "Suppressed result"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "src/other.py"}
                                }
                            }
                        ],
                        "suppressions": [{"kind": "external", "status": "accepted"}],
                    },
                ],
            }
        ],
    }


class NormalizeSarifTests(unittest.TestCase):
    def test_normalizes_and_deduplicates_supplied_fingerprints(self) -> None:
        summary = sarif.normalize_sarif(sample_sarif(), "sample.sarif")

        self.assertEqual(summary["raw_result_count"], 3)
        self.assertEqual(summary["normalized_result_count"], 2)
        self.assertEqual(summary["duplicates_collapsed"], 1)
        first = summary["results"][0]
        self.assertEqual(first["rule_id"], "EX001")
        self.assertEqual(first["baseline_state"], "new")
        self.assertEqual(first["level"], "error")
        self.assertEqual(first["identity_source"], "supplied fingerprint")
        self.assertEqual(first["duplicate_count"], 2)
        self.assertEqual(first["verification_status"], "unverified")

    def test_retains_suppression_state(self) -> None:
        summary = sarif.normalize_sarif(sample_sarif())
        suppressed = next(item for item in summary["results"] if item["rule_id"] == "EX002")

        self.assertTrue(suppressed["is_suppressed"])
        self.assertEqual(suppressed["suppression"], "external:accepted")
        self.assertEqual(summary["suppressed_count"], 1)

    def test_retains_rejected_suppression_without_counting_it_as_active(self) -> None:
        data = sample_sarif()
        data["runs"][0]["results"][2]["suppressions"][0]["status"] = "rejected"

        summary = sarif.normalize_sarif(data)
        result = next(item for item in summary["results"] if item["rule_id"] == "EX002")

        self.assertFalse(result["is_suppressed"])
        self.assertEqual(result["suppression"], "external:rejected")
        self.assertEqual(summary["suppressed_count"], 0)
        self.assertEqual(summary["suppression_metadata_count"], 1)

    def test_null_suppression_state_remains_unavailable(self) -> None:
        data = sample_sarif()
        data["runs"][0]["results"][2]["suppressions"] = None

        summary = sarif.normalize_sarif(data)
        result = next(item for item in summary["results"] if item["rule_id"] == "EX002")

        self.assertEqual(result["suppression"], "unavailable")
        self.assertFalse(result["is_suppressed"])
        self.assertEqual(summary["suppression_metadata_count"], 0)

    def test_retains_all_locations_and_suppression_justification(self) -> None:
        data = sample_sarif()
        result = data["runs"][0]["results"][2]
        result["locations"].append(
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": "src/secondary.py"},
                    "region": {"startLine": 27},
                },
                "logicalLocations": [{"name": "secondary"}],
            }
        )
        result["suppressions"][0]["justification"] = "Accepted by security review"

        summary = sarif.normalize_sarif(data)
        suppressed = next(item for item in summary["results"] if item["rule_id"] == "EX002")

        self.assertEqual(len(suppressed["locations"]), 2)
        self.assertEqual(suppressed["locations"][1]["uri"], "src/secondary.py")
        self.assertEqual(suppressed["locations"][1]["line"], 27)
        self.assertEqual(suppressed["locations"][1]["logical_name"], "secondary")
        self.assertEqual(
            suppressed["suppressions"][0]["justification"],
            "Accepted by security review",
        )

    def test_resolves_extension_rule_components_without_collisions(self) -> None:
        data = {
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {"name": "CompositeScanner", "rules": []},
                        "extensions": [
                            {
                                "name": "SecurityRules",
                                "rules": [
                                    {
                                        "id": "DUP001",
                                        "name": "Security rule",
                                        "defaultConfiguration": {
                                            "level": "error",
                                            "rank": 90.0,
                                        },
                                    }
                                ],
                            },
                            {
                                "name": "StyleRules",
                                "rules": [
                                    {
                                        "id": "DUP001",
                                        "name": "Style rule",
                                        "defaultConfiguration": {"level": "note"},
                                    }
                                ],
                            },
                        ],
                    },
                    "results": [
                        {
                            "rule": {
                                "id": "DUP001",
                                "index": 0,
                                "toolComponent": {"index": 0},
                            },
                            "message": {"text": "Security result"},
                            "partialFingerprints": {"stable/v1": "same"},
                        },
                        {
                            "rule": {
                                "id": "DUP001",
                                "index": 0,
                                "toolComponent": {"index": 1},
                            },
                            "message": {"text": "Style result"},
                            "partialFingerprints": {"stable/v1": "same"},
                        },
                    ],
                }
            ],
        }

        summary = sarif.normalize_sarif(data)

        self.assertEqual(summary["normalized_result_count"], 2)
        by_component = {item["rule_component"]: item for item in summary["results"]}
        self.assertEqual(by_component["SecurityRules"]["rule_name"], "Security rule")
        self.assertEqual(by_component["SecurityRules"]["level"], "error")
        self.assertEqual(by_component["SecurityRules"]["rank"], 90.0)
        self.assertEqual(by_component["StyleRules"]["rule_name"], "Style rule")

    def test_component_name_alone_does_not_select_an_extension(self) -> None:
        data = {
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Scanner",
                            "rules": [{"id": "DRIVER001", "name": "Driver rule"}],
                        },
                        "extensions": [
                            {
                                "name": "Extension",
                                "rules": [{"id": "EXT001", "name": "Extension rule"}],
                            }
                        ],
                    },
                    "results": [
                        {
                            "rule": {
                                "id": "DRIVER001",
                                "index": 0,
                                "toolComponent": {"name": "Extension"},
                            },
                            "message": {"text": "Driver result"},
                        }
                    ],
                }
            ],
        }

        result = sarif.normalize_sarif(data)["results"][0]

        self.assertEqual(result["rule_component_kind"], "driver")
        self.assertEqual(result["rule_name"], "Driver rule")

    def test_does_not_deduplicate_across_independent_runs(self) -> None:
        data = sample_sarif()
        data["runs"].append(deepcopy(data["runs"][0]))

        summary = sarif.normalize_sarif(data)

        self.assertEqual(summary["raw_result_count"], 6)
        self.assertEqual(summary["normalized_result_count"], 4)
        self.assertEqual(summary["duplicates_collapsed"], 2)

    def test_markdown_states_that_results_are_unverified(self) -> None:
        rendered = sarif.render_markdown(sarif.normalize_sarif(sample_sarif()), limit=100)

        self.assertIn("Normalization only", rendered)
        self.assertIn("ExampleScanner/EX001", rendered)
        self.assertIn("Duplicates collapsed: 1", rendered)
        self.assertIn("Actively suppressed results: 1", rendered)

    def test_markdown_escapes_untrusted_control_and_link_markup(self) -> None:
        data = sample_sarif()
        data["runs"][0]["results"][0]["message"]["text"] = (
            "\x1b\u009b\u202e[click](https://example.invalid)|`code`"
        )

        rendered = sarif.render_markdown(sarif.normalize_sarif(data), limit=100)

        self.assertNotIn("\x1b", rendered)
        self.assertNotIn("\u009b", rendered)
        self.assertNotIn("\u202e", rendered)
        self.assertIn("\\\\x1b\\\\x9b\\\\u202e\\[click\\](https://example.invalid)\\|\\`code\\`", rendered)

    def test_load_rejects_unsupported_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.sarif"
            path.write_text(json.dumps({"version": "2.0.0", "runs": []}), encoding="utf-8")

            with self.assertRaises(sarif.SarifError):
                sarif.load_sarif(path)

    def test_load_accepts_null_runs_allowed_by_sarif(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.sarif"
            path.write_text(
                json.dumps({"version": "2.1.0", "runs": None}),
                encoding="utf-8",
            )

            summary = sarif.normalize_sarif(sarif.load_sarif(path))

            self.assertEqual(summary["runs_state"], "population_failed")
            self.assertEqual(summary["runs"], [])
            self.assertEqual(summary["raw_result_count"], 0)
            self.assertIn("attempted to populate runs but failed", summary["notice"])
            self.assertIn(
                r"Runs state: `population\_failed`",
                sarif.render_markdown(summary, limit=100),
            )

    def test_empty_runs_remains_distinct_from_failed_population(self) -> None:
        summary = sarif.normalize_sarif({"version": "2.1.0", "runs": []})

        self.assertEqual(summary["runs_state"], "empty")
        self.assertNotIn("attempted to populate runs but failed", summary["notice"])

    def test_load_rejects_missing_runs_property(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.sarif"
            path.write_text(json.dumps({"version": "2.1.0"}), encoding="utf-8")

            with self.assertRaises(sarif.SarifError):
                sarif.load_sarif(path)

    def test_load_rejects_nonstandard_json_constants(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.sarif"
            path.write_text(
                '{"version":"2.1.0","runs":[],"invalid":NaN}',
                encoding="utf-8",
            )

            with self.assertRaises(sarif.SarifError):
                sarif.load_sarif(path)


if __name__ == "__main__":
    unittest.main()
