#!/usr/bin/env python3
"""Validate repository hygiene and direct reference links for this skill."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


REQUIRED_PATHS = {
    ".gitignore",
    ".github/workflows/ci.yml",
    "LICENSE",
    "SKILL.md",
    "README.md",
    "README.zh-CN.md",
    "agents/openai.yaml",
    "references/execution-safety.md",
    "references/artifact-resilience-review.md",
    "references/intake-protocol.md",
    "references/language-thresholds.md",
    "references/machine-report-protocol.md",
    "references/metric-rubric.md",
    "references/report-templates.md",
    "references/review-dimensions.md",
    "references/scoring-and-prioritization.md",
    "references/security-and-supply-chain.md",
    "references/standards-map.md",
    "references/verification-strategy.md",
    "scripts/summarize_code_health.py",
    "scripts/summarize_sarif.py",
    "scripts/validate_package.py",
    "tests/fixtures/code-health.json",
    "tests/fixtures/sample.sarif",
    "tests/test_summarize_code_health.py",
    "tests/test_summarize_sarif.py",
    "tests/test_validate_package.py",
}
BANNED_NAMES = {
    ".DS_Store",
    "Archive.zip",
    "__MACOSX",
    "__pycache__",
    ".pytest_cache",
}
ALLOWED_TOP_LEVEL = {
    ".gitignore",
    ".github",
    "LICENSE",
    "NOTICE",
    "README.md",
    "README.zh-CN.md",
    "SKILL.md",
    "agents",
    "references",
    "scripts",
    "tests",
}
IGNORED_CHECKOUT_ENTRIES = {".git"}
REFERENCE_PATTERN = re.compile(r"`references/([a-z0-9-]+\.md)`")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
REQUIRED_COPYRIGHT = "Copyright (c) 2026 Marstlantis"
REQUIRED_REPOSITORY_URL = "https://github.com/Marstlantis/AI-Code-Health-Review"
README_PROCESS_PATTERNS = {
    "full Git object ID": re.compile(r"\b[0-9a-f]{40}\b", re.IGNORECASE),
    "maintenance narrative": re.compile(
        r"\breviewed\s+at\s+commit\b|\bmaintenance\s+baseline\b|"
        r"\brefreshed\s+locally\b|\u7ef4\u62a4\u57fa\u7ebf|"
        r"\u5728\u63d0\u4ea4\s+`?[0-9a-f]{7,40}",
        re.IGNORECASE,
    ),
}


def _iter_package_paths(root: Path):
    for current, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        if current_path == root:
            dirnames[:] = [
                name for name in dirnames if name not in IGNORED_CHECKOUT_ENTRIES
            ]
        for name in dirnames:
            yield current_path / name
        for name in filenames:
            if current_path == root and name in IGNORED_CHECKOUT_ENTRIES:
                continue
            yield current_path / name


def _read_text(path: Path, root: Path, errors: list[str]) -> str | None:
    if path.is_symlink():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read UTF-8 text file: {path.relative_to(root)}: {exc}")
        return None


def _terminal_safe(value: str) -> str:
    return value.encode("unicode_escape", "backslashreplace").decode("ascii")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"not a directory: {root}"]

    for relative in sorted(REQUIRED_PATHS):
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    for entry in root.iterdir():
        if entry.name in IGNORED_CHECKOUT_ENTRIES:
            continue
        if entry.name not in ALLOWED_TOP_LEVEL:
            errors.append(f"unexpected top-level entry: {entry.name}")

    package_paths = list(_iter_package_paths(root))
    for path in package_paths:
        if path.is_symlink():
            errors.append(f"symbolic link is not portable: {path.relative_to(root)}")
        if path.name in BANNED_NAMES:
            errors.append(f"banned artifact: {path.relative_to(root)}")
        if path.is_file() and (path.suffix in {".pyc", ".pyo", ".zip"}):
            errors.append(f"banned generated/archive file: {path.relative_to(root)}")

    skill_path = root / "SKILL.md"
    if skill_path.is_file():
        skill_text = _read_text(skill_path, root, errors)
        if skill_text is not None:
            for reference in sorted(set(REFERENCE_PATTERN.findall(skill_text))):
                relative = f"references/{reference}"
                if not (root / relative).is_file():
                    errors.append(f"SKILL.md references missing file: {relative}")

    readme = root / "README.md"
    readme_zh = root / "README.zh-CN.md"
    license_path = root / "LICENSE"
    if license_path.is_file():
        license_text = _read_text(license_path, root, errors)
        if license_text is not None and REQUIRED_COPYRIGHT not in license_text:
            errors.append(f"LICENSE must contain: {REQUIRED_COPYRIGHT}")
    if readme.is_file():
        readme_text = _read_text(readme, root, errors)
        if readme_text is not None:
            if "README.zh-CN.md" not in readme_text:
                errors.append("README.md does not link to README.zh-CN.md")
            if "Marstlantis" not in readme_text:
                errors.append("README.md does not name the copyright holder Marstlantis")
            if REQUIRED_REPOSITORY_URL not in readme_text:
                errors.append(
                    f"README.md must use the canonical repository URL: "
                    f"{REQUIRED_REPOSITORY_URL}"
                )
            for label, pattern in README_PROCESS_PATTERNS.items():
                if pattern.search(readme_text):
                    errors.append(f"README.md contains prohibited {label}")
    if readme_zh.is_file():
        readme_zh_text = _read_text(readme_zh, root, errors)
        if readme_zh_text is not None:
            if "README.md" not in readme_zh_text:
                errors.append("README.zh-CN.md does not link to README.md")
            if "Marstlantis" not in readme_zh_text:
                errors.append(
                    "README.zh-CN.md does not name the copyright holder Marstlantis"
                )
            if REQUIRED_REPOSITORY_URL not in readme_zh_text:
                errors.append(
                    f"README.zh-CN.md must use the canonical repository URL: "
                    f"{REQUIRED_REPOSITORY_URL}"
                )
            for label, pattern in README_PROCESS_PATTERNS.items():
                if pattern.search(readme_zh_text):
                    errors.append(f"README.zh-CN.md contains prohibited {label}")

    for markdown_path in package_paths:
        if not markdown_path.is_file() or markdown_path.suffix != ".md":
            continue
        text = _read_text(markdown_path, root, errors)
        if text is None:
            continue
        for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (markdown_path.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(
                    f"local Markdown link escapes repository: "
                    f"{markdown_path.relative_to(root)} -> {raw_target}"
                )
                continue
            if not resolved.exists():
                errors.append(
                    f"broken local Markdown link: "
                    f"{markdown_path.relative_to(root)} -> {raw_target}"
                )

    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Skill/repository root (defaults to this script's parent skill)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {_terminal_safe(error)}", file=sys.stderr)
        return 1
    print("Package hygiene validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
