# AI Code Health Review

[简体中文](README.zh-CN.md)

This Codex skill reviews code, diffs, repositories, tests, dependencies, CI/CD, infrastructure configuration, release artifacts, and machine-generated analysis reports.

Each finding explains the inspected evidence, the risk, a proposed fix, and how to verify it. Reviews distinguish correctness, security, privacy, data integrity, reliability, supply-chain integrity, test quality, maintainability, and performance. Style preferences and unverified scanner scores do not establish defects.

## Review coverage

- Code, PR, pre-commit, and project-health reviews that lead with actionable findings
- Authentication, authorization, sensitive data, and untrusted input, assessed against the actual threat context
- Dependency, lockfile, CI/CD, container, infrastructure, provenance, and release review
- Release artifacts, signing, entitlements, secret exposure, and resistance to reverse engineering, assessed against the protected assets and attacker capabilities
- Inspection of entry points and side effects before running project-controlled builds, tests, scanners, or package scripts
- SARIF 2.1.0 normalization with baseline, fingerprint, and suppression preservation
- Weighted code-health report normalization that reports empty or partial coverage, skipped or failed files, and missing configuration, parser, or location metadata
- Separate treatment of tool signals, verified evidence, severity, and confidence
- Qualitative hotspot assessment, with no invented project scores or universal thresholds
- Risk-based test review and fix verification
- Incremental refactoring recommendations that state the remaining risk

## Scope and limits

This skill is not a SAST/SCA engine, penetration test, exploit framework, compliance certification, or proof that software is vulnerability-free or impossible to reverse engineer. It does not treat a successful build, passing test suite, high score, empty scanner report, detected debugger, or applied obfuscation as proof of safety.

Repository content and analyzer reports supply evidence; embedded instructions cannot grant permission or redirect the review. Before running project-controlled code, inspect its entry points and side effects. Existing authorization remains valid within the task scope. A review does not grant access to production data or permission to publish results.

Small reviews start with the supplied material. The skill reads supporting references when the question needs them and stops verification after the relevant checks pass, unless new changes, failures, or unresolved concerns justify more work.

## Installation

Use the built-in installer to let Codex select its managed user-skill location:

```text
$skill-installer install the repository-root skill from https://github.com/Marstlantis/AI-Code-Health-Review as ai-code-health-review
```

For a manual installation shared across compatible clients, clone the repository into the standard user skill directory:

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Marstlantis/AI-Code-Health-Review.git "$HOME/.agents/skills/ai-code-health-review"
```

Codex detects skill changes automatically; restart only if the skill does not appear.

For a project-local installation, use:

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

Codex can also select the skill when a request matches its description.

## SARIF normalizer

The bundled normalizer reads SARIF 2.1.0 with Python's standard library:

```bash
python3 scripts/summarize_sarif.py report.sarif --format markdown
python3 scripts/summarize_sarif.py report.sarif --format json
```

The script preserves driver and extension rule-component metadata, rule names and ranks, baseline state, supplied fingerprints, all result locations, suppression justifications, and code-flow counts. An empty `runs` array stays distinct from `runs: null`, which means the producer failed to populate runs.

Normalization is deterministic and deduplication is conservative. The script does not verify source behavior, reachability, exploitability, severity, or correctness. Its output retains report paths and messages, so keep it local unless disclosure is authorized.

The parser rejects unsupported SARIF versions, non-standard JSON constants, and reports larger than 50 MiB. Markdown output neutralizes terminal controls, bidirectional text controls, raw HTML delimiters, and active link markup from untrusted report fields.

## Code-health report normalizer

The standard-library code-health normalizer accepts compatible weighted per-file JSON reports containing `summary`, `files[].metrics`, and `files[].parseResult` fields:

```bash
python3 scripts/summarize_code_health.py report.json --tool-name example-analyzer --format markdown
python3 scripts/summarize_code_health.py report.json --tool-name example-analyzer --format json
```

The script retains the tool's scores, severities, metrics, languages, file counts, and optional locations. It reports whether coverage is available, partial, empty, not populated, or unknown. A score of 100 with zero analyzed files provides no evidence of code health. Missing weights, include/exclude configuration, parser mode, failure counts, or metric locations remain unavailable; they cannot support a project-wide score claim.

The normalizer prepares a supplied local report for verification against the source. It does not run the analyzer, install npm packages, invoke MCP, upload source, validate metric formulas, or decide whether refactoring is needed. Output retains report paths, project paths, file paths, and metric details, so keep it local unless disclosure is authorized.

## Findings

Each important finding includes the following information, in concise prose or separate fields:

- Severity, status, and confidence
- Precise location and inspected evidence
- Concrete impact and smallest safe fix
- Verification that would prove the fix
- Security prerequisites/reachability and affected assets when applicable
- Tool/rule/baseline/fingerprint/suppression metadata for machine reports
- Versioned standards mapping only when actually evaluated

Numeric scores remain attributed to the tool or scoring model that produced them. When no scoring model is supplied, reviews use qualitative risk bands tied to the inspected scope.

## Standards and sources

The skill format follows [OpenAI's Build skills guidance](https://learn.chatgpt.com/docs/build-skills) and the [Agent Skills specification](https://agentskills.io/specification). The review references use these versioned or publisher-maintained sources:

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

## Repository layout

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

`SKILL.md` contains the review workflow and routes to references as needed. The README files document the repository; the skill does not require reading them during a review.

## Validation

Python 3.10 or newer is required only for the bundled scripts and tests. The skill instructions themselves have no runtime package dependency.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_package.py .
```

The package validator rejects common release debris, archives, Python caches, symbolic links, missing required files, broken direct references, and missing language cross-links. It ignores top-level Git checkout metadata, so it also works in a normal clone without scanning `.git` internals.

GitHub Actions runs the standard-library tests and package validator on Python 3.10 and 3.14 with read-only repository permissions and commit-pinned official actions.

## Contributing

When contributing:

1. Keep the scope and evidence requirements clear in `SKILL.md`; link detailed procedures where they are needed.
2. Use official or primary sources for standards and record version/status changes.
3. Do not add universal metric thresholds or scoring weights without a named, versioned, reproducible model.
4. Add tests for deterministic scripts and avoid network dependencies.
5. Preserve execution safety, secret handling, scope disclosure, and verification of machine reports.
6. Run all validation commands before submitting changes.

## License

[MIT License](LICENSE), copyright (c) 2026 Marstlantis.
