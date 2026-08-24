from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_package.py"
SPEC = importlib.util.spec_from_file_location("validate_package", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidatePackageTests(unittest.TestCase):
    def make_package(self, root: Path) -> None:
        for relative in validator.REQUIRED_PATHS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")
        (root / "SKILL.md").write_text(
            "---\nname: sample\ndescription: sample\n---\n",
            encoding="utf-8",
        )
        (root / "README.zh-CN.md").write_text(
            "[English](README.md)\n[许可证](LICENSE)\nMarstlantis\n"
            + validator.REQUIRED_REPOSITORY_URL
            + "\n",
            encoding="utf-8",
        )
        (root / "LICENSE").write_text(
            validator.REQUIRED_COPYRIGHT + "\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text(
            "[简体中文](README.zh-CN.md)\n[License](LICENSE)\nMarstlantis\n"
            + validator.REQUIRED_REPOSITORY_URL
            + "\n",
            encoding="utf-8",
        )

    def test_accepts_checkout_metadata_without_traversing_git_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_package(root)
            git_object = root / ".git" / "objects" / "Archive.zip"
            git_object.parent.mkdir(parents=True)
            git_object.write_text("not package content", encoding="utf-8")

            self.assertEqual(validator.validate(root), [])

    def test_requires_license_and_regression_tests(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_package(root)
            (root / "LICENSE").unlink()
            (root / "references" / "artifact-resilience-review.md").unlink()
            (root / "scripts" / "summarize_code_health.py").unlink()
            (root / "tests" / "test_summarize_sarif.py").unlink()

            errors = validator.validate(root)

            self.assertIn("missing required file: LICENSE", errors)
            self.assertIn(
                "missing required file: references/artifact-resilience-review.md",
                errors,
            )
            self.assertIn(
                "missing required file: scripts/summarize_code_health.py",
                errors,
            )
            self.assertIn(
                "missing required file: tests/test_summarize_sarif.py",
                errors,
            )

    def test_rejects_symlinks_even_when_the_target_exists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "package"
            root.mkdir()
            self.make_package(root)
            target = base / "outside.md"
            target.write_bytes(b"\xffnot-utf-8")
            link = root / "references" / "linked.md"
            try:
                link.symlink_to(target)
            except (NotImplementedError, OSError):
                self.skipTest("symbolic links are not available")

            errors = validator.validate(root)

            self.assertTrue(
                any(error.startswith("symbolic link is not portable:") for error in errors)
            )
            self.assertFalse(any("cannot read UTF-8 text file" in error for error in errors))

    def test_rejects_wrong_copyright_and_readme_process_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_package(root)
            (root / "LICENSE").write_text(
                "Copyright (c) 2026 Previous Owner\n",
                encoding="utf-8",
            )
            with (root / "README.md").open("a", encoding="utf-8") as stream:
                object_id = ("0123456789abcdef" * 2) + "01234567"
                stream.write("reviewed at " + "commit " + object_id + "\n")

            errors = validator.validate(root)

            self.assertIn(
                f"LICENSE must contain: {validator.REQUIRED_COPYRIGHT}",
                errors,
            )
            self.assertIn("README.md contains prohibited full Git object ID", errors)
            self.assertIn("README.md contains prohibited maintenance narrative", errors)

    def test_rejects_noncanonical_repository_url(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_package(root)
            readme = root / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8").replace(
                    validator.REQUIRED_REPOSITORY_URL,
                    "https://github.com/PreviousOwner/AI-Code-Health-Review",
                ),
                encoding="utf-8",
            )

            errors = validator.validate(root)

            self.assertIn(
                "README.md must use the canonical repository URL: "
                + validator.REQUIRED_REPOSITORY_URL,
                errors,
            )


if __name__ == "__main__":
    unittest.main()
