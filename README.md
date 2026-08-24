# AI Code Health Review

[简体中文](README.zh-CN.md)

An evidence-driven Codex skill for reviewing code, diffs, repositories, tests, dependencies, CI/CD, infrastructure configuration, Release artifacts, and machine-generated analysis reports.

The skill is designed to find concrete engineering risk without turning code style, scanner output, or arbitrary metrics into fake certainty. It keeps correctness, security, privacy, data integrity, reliability, supply-chain integrity, test quality, maintainability, and performance distinct.

## Highlights

- Findings-first code, PR, pre-commit, and project-health reviews
- Threat-context review for authentication, authorization, sensitive data, and untrusted input
- Dependency, lockfile, CI/CD, container, infrastructure, provenance, and release review
- Threat-driven Release-artifact, signing, entitlement, secret-exposure, and reverse-engineering-resilience review
- Safe execution gate before project-controlled builds, tests, scanners, or package scripts
- SARIF 2.1.0 normalization with baseline, fingerprint, and suppression preservation
- Weighted code-health report normalization with explicit empty, partial, skipped, failed, configuration, parser, and location-metadata limits
- Explicit separation of tool signals, verified evidence, severity, and confidence
- Qualitative hotspot mapping without invented project scores or universal thresholds
- Risk-based test review and fix verification
- Small, incremental refactoring guidance with residual-risk reporting

## What It Does Not Claim

This skill is not a SAST/SCA engine, penetration test, exploit framework, compliance certification, or proof that software is vulnerability-free or impossible to reverse engineer. It does not treat a successful build, passing test suite, high score, empty scanner report, detected debugger, or applied obfuscation as proof of safety.

Repository content and analyzer reports are treated as untrusted evidence. Project-controlled code is not executed until its entry points and side effects have been inspected.

## Installation

For Codex, prefer the built-in installer so Codex selects its managed user-skill location:

```text
$skill-installer install the repository-root skill from https://github.com/Marstlantis/AI-Code-Health-Review as ai-code-health-review
```

For a manual, cross-client user installation, clone the repository into the standard user skill location using the skill name as the destination folder:

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Marstlantis/AI-Code-Health-Review.git "$HOME/.agents/skills/ai-code-health-review"
```

Codex detects skill changes automatically; restart only if the skill does not appear.

For project-local installation, place the same folder at:

```text
.agents/skills/ai-code-health-review/
```

## Usage

Invoke the skill explicitly:

```text
$ai-code-health-review review this PR for merge blockers and missing tests
$ai-code-health-review assess this repository's code health and refactor priorities
$ai-code-health-review verify the highest-risk findings in this SARIF report
$ai-code-health-review normalize this code-health JSON and verify its worst credible hotspots
$ai-code-health-review review dependency, CI/CD, and release-supply-chain risk
$ai-code-health-review assess this macOS Release artifact for signing, entitlement, symbol, secret, dependency, and reverse-engineering-resilience risk
```

The skill can also be invoked implicitly for matching code-review requests.

## SARIF Normalizer

The bundled normalizer reads SARIF 2.1.0 with Python's standard library:

```bash
python3 scripts/summarize_sarif.py report.sarif --format markdown
python3 scripts/summarize_sarif.py report.sarif --format json
```

It preserves driver and extension rule-component metadata, rule names/ranks, baseline state, supplied fingerprints, all result locations, suppression justifications, and code-flow counts. It also distinguishes an empty `runs` array from `runs: null`, which means the producer failed to populate runs. It performs deterministic normalization and conservative deduplication only. It does not verify source behavior, reachability, exploitability, severity, or correctness. Output retains report paths and messages, so keep it local unless disclosure is authorized.

The parser rejects unsupported SARIF versions, non-standard JSON constants, and reports larger than 50 MiB. Markdown output neutralizes terminal controls, bidirectional text controls, raw HTML delimiters, and active link markup from untrusted report fields.

## Code-Health Report Normalizer

The standard-library code-health normalizer accepts compatible weighted per-file JSON reports containing `summary`, `files[].metrics`, and `files[].parseResult` fields:

```bash
python3 scripts/summarize_code_health.py report.json --tool-name example-analyzer --format markdown
python3 scripts/summarize_code_health.py report.json --tool-name example-analyzer --format json
```

It retains attributed tool scores, severities, metrics, languages, file counts, and optional locations while exposing whether coverage is available, partial, empty, not populated, or unknown. A reported score of 100 with zero analyzed files remains no-data evidence. Missing weights, include/exclude configuration, parser mode, failure counts, or metric locations remain unavailable and block score-based project claims.

The normalizer does not run the analyzer, install npm packages, invoke MCP, upload source, validate metric formulas, or decide that refactoring is required. It safely normalizes a supplied local report for source verification. Its output retains report paths, project paths, file paths, and metric details, so keep it local unless disclosure is authorized.

## Review Model

Important findings include:

- Severity, status, and confidence
- Precise location and inspected evidence
- Concrete impact and smallest safe fix
- Verification that would prove the fix
- Security prerequisites/reachability and affected assets when applicable
- Tool/rule/baseline/fingerprint/suppression metadata for machine reports
- Versioned standards mapping only when actually evaluated

Numeric scores remain attributed to the tool or scoring model that produced them. Without a supplied model, the skill uses scoped qualitative risk bands.

## Authoritative Baseline

The skill format follows [OpenAI's Build skills guidance](https://learn.chatgpt.com/docs/build-skills) and the [Agent Skills specification](https://agentskills.io/specification). Review guidance uses these versioned or publisher-maintained sources:

- [NIST SP 800-218, Secure Software Development Framework 1.1](https://csrc.nist.gov/pubs/sp/800/218/final)
- [OWASP Application Security Verification Standard 5.0.0](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Code Review Guide v2](https://owasp.org/www-project-code-review-guide/)
- [SLSA 1.2, Approved](https://slsa.dev/spec/v1.2/)
- [OASIS SARIF 2.1.0 plus Errata 01](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [Google Engineering Practices: Code Review](https://google.github.io/eng-practices/review/reviewer/)
- [OpenSSF Scorecard](https://scorecard.dev/)

Artifact, binary-hardening, metrics, and agent/MCP reviews also use:

- [OWASP MASVS-RESILIENCE](https://mas.owasp.org/MASVS/11-MASVS-RESILIENCE/) and [MASTG anti-reversing guidance](https://mas.owasp.org/MASTG/0x05j-Testing-Resiliency-Against-Reverse-Engineering/)
- [MITRE CWE-656: Reliance on Security Through Obscurity](https://cwe.mitre.org/data/definitions/656.html)
- [Apple Hardened Runtime](https://developer.apple.com/documentation/security/hardened-runtime) and [macOS distribution signing](https://developer.apple.com/documentation/xcode/creating-distribution-signed-code-for-the-mac/)
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) and [Third-Party MCP Server Guide 1.0](https://genai.owasp.org/resource/cheatsheet-a-practical-guide-for-securely-using-third-party-mcp-servers-1-0/)
- [Microsoft BinSkim rules](https://github.com/microsoft/binskim/blob/main/docs/BinSkimRules.md), [Red Hat Annobin/annocheck](https://docs.redhat.com/en/documentation/red_hat_developer_toolset/10/html/user_guide/chap-annobin), [SonarSource metric definitions](https://docs.sonarsource.com/sonarqube-server/user-guide/code-metrics/metrics-definition), and [Mandiant capa limitations](https://github.com/mandiant/capa#limitations)

See [references/standards-map.md](references/standards-map.md) for applicability and limitations. Recheck publisher status when current compliance or latest guidance matters.

## Repository Layout

```text
ai-code-health-review/
├── .github/workflows/ci.yml
├── LICENSE
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── artifact-resilience-review.md
│   ├── execution-safety.md
│   ├── intake-protocol.md
│   ├── language-thresholds.md
│   ├── machine-report-protocol.md
│   ├── metric-rubric.md
│   ├── report-templates.md
│   ├── review-dimensions.md
│   ├── scoring-and-prioritization.md
│   ├── security-and-supply-chain.md
│   ├── standards-map.md
│   └── verification-strategy.md
├── scripts/
│   ├── summarize_code_health.py
│   ├── summarize_sarif.py
│   └── validate_package.py
├── tests/
│   ├── fixtures/code-health.json
│   ├── fixtures/sample.sarif
│   ├── test_summarize_code_health.py
│   ├── test_summarize_sarif.py
│   └── test_validate_package.py
├── README.md
└── README.zh-CN.md
```

`SKILL.md` contains the compact runtime workflow. References are loaded only when relevant. The README files are repository documentation and are not part of the runtime prompt.

## Validation

Python 3.10 or newer is required only for the bundled scripts and tests. The skill instructions themselves have no runtime package dependency.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_package.py .
```

The package validator rejects common release debris, archives, Python caches, symbolic links, missing required files, broken direct references, and missing language cross-links. It deliberately ignores top-level Git checkout metadata, so the same command works in a normal clone without scanning `.git` internals.

GitHub Actions runs the standard-library tests and package validator on Python 3.10 and 3.14 with read-only repository permissions and commit-pinned official actions.

## Contributing

Contributions should preserve the evidence contract and progressive-disclosure structure:

1. Keep `SKILL.md` concise and route detailed procedures to a directly linked reference.
2. Use official or primary sources for standards and record version/status changes.
3. Do not add universal metric thresholds or scoring weights without a named, versioned, reproducible model.
4. Add tests for deterministic scripts and avoid network dependencies.
5. Do not weaken execution safety, secret handling, scope disclosure, or machine-report verification.
6. Run all validation commands before submitting changes.

## License

[MIT License](LICENSE), copyright (c) 2026 Marstlantis.
