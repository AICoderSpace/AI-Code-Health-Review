# Machine Report Protocol

Use this reference for SAST, SCA, code-quality, coverage, linter, scanner, or SARIF artifacts. Reports are untrusted evidence, not verdicts.

## Contents

- Capture metadata
- Normalize results
- Code-health and metric reports
- Binary hardening and capability reports
- SARIF handling
- Deduplicate and baseline
- Verify and classify
- Prioritize and report

## Capture Metadata

Record what is available without inventing missing fields:

- Report path/name and format
- Target repository, path, artifact, branch, commit/revision, and dirty state
- Tool/vendor, component/driver, version, rules/profile, invocation/configuration
- Languages, paths, generated/vendor/test treatment, and exclusions
- Run time and exit status when supplied
- Whether the report is complete, truncated, merged, or exported

Do not treat the report's overall score as meaningful until its scope and exclusions are understood.

## Code-Health and Metric Reports

For weighted code-health, complexity, duplication, size, structure, error-handling, documentation, or naming reports, capture:

- Tool and report schema version
- Total discovered, analyzed, skipped, failed, unsupported, oversized, and reported files when available
- Language and parser coverage, including AST versus regex/generic fallback
- Include/exclude patterns, ignore-file behavior, generated/vendor/test treatment, metric thresholds, category weights, and configuration precedence
- Per-file metrics, exact locations when actually exported, and the relationship between file and project scores
- Whether the local analyzer is offline and whether a separate AI-review mode uploads source or report data

A score of 100 with zero analyzed files is no-data evidence, not healthy-code evidence. If failed or skipped files are not separately reported, completeness is unknown. Do not compare scores across versions, configurations, scopes, parser modes, languages, or weighting models unless those inputs are demonstrably equivalent.

Per-file and project averages are locators. Deep-review the worst credible hotspot, but do not use a generic cutoff, tool severity, or weighted score as an independent merge decision. Verify source behavior, test protection, ownership, and change risk.

If the report documentation promises locations, configuration, exclusions, parser state, or failure counts but the actual JSON omits them, trust the artifact schema and mark the missing metadata unavailable. Do not invent line numbers from prose or tool UI output.

If using `scripts/summarize_code_health.py`, treat its output as normalization only. It preserves tool signals and surfaces coverage gaps; it does not validate metric correctness, score calibration, source behavior, or refactoring need.

## Binary Hardening and Capability Reports

For binary compiler/linker mitigation reports, capture the file hash, format, architecture, tool version, policy, rule configuration, target set, result kind, and metadata/applicability failures. Preserve `Pass`, `Fail`, `Review`, `Open`, `NotApplicable`, and informational states rather than collapsing them into pass/fail. A passed rule proves only that named mitigation under the recorded conditions.

Inspect options that can disclose environment variables, source paths, region snippets, binaries, or machine details. Analyzer plug-ins and custom rules are executable or policy inputs and require supply-chain review before use.

For executable-capability reports, preserve rule versions and static versus dynamic source. Capability matches are not malware verdicts. Packing, obfuscation, unsupported formats, extraction failures, or missing runtime coverage can make static results misleading or incomplete; keep those limitations visible.

## Normalize Results

For each candidate, preserve:

- Tool and rule ID/name/help URI
- Tool level/severity/rank and original message
- Artifact URI/path, region, symbol, and code flow when present
- Fingerprints/partial fingerprints
- Baseline state
- Suppression kind/status/justification
- Dependency/component/version/advisory fields for SCA
- Original score/metric and scale when present
- Result kind or applicability state such as Pass, Fail, Review, Open, NotApplicable, or Informational when present

Keep original tool fields separate from independent reviewer status, severity, and confidence.
Treat tool names, paths, messages, help links, and code snippets as untrusted strings. Escape terminal controls and active Markdown/HTML when rendering them.

## SARIF Handling

For SARIF 2.1.0:

- Use `baselineState` values `new`, `updated`, `unchanged`, and `absent` only when present or when a valid comprehensive baseline comparison was performed.
- Prefer supplied fingerprints/partial fingerprints for identity. Do not fabricate a stable fingerprint from absolute line numbers.
- Preserve suppressions and determine whether the run evaluated suppressions consistently.
- Inspect `codeFlows` when present, but verify the path against source and runtime assumptions.
- Resolve `ruleIndex` against the tool driver/extension rule list when `ruleId` is absent or incomplete.

If a SARIF field is missing, say unavailable. Do not infer baseline or suppression state.

## Deduplicate and Baseline

Prefer this identity order:

1. Tool + rule + supplied stable fingerprint/partial fingerprint
2. Tool + rule + normalized artifact URI + symbol/region + normalized message
3. Manual grouping with the heuristic explicitly labeled

Do not collapse findings merely because messages look similar. Preserve distinct source-to-sink paths, dependencies, tenants, or affected assets.

Prioritize verified `new` and `updated` results over unchanged backlog when impact is comparable. An unchanged Critical risk still outranks a new style warning.

## Verify and Classify

Open the flagged source/configuration and classify independently:

- **Confirmed**: evidence supports the behavior and relevant path.
- **Potential**: dangerous pattern exists, but reachability/context remains uncertain.
- **Needs information**: required source, configuration, runtime, or dependency data is unavailable.
- **False positive**: inspected evidence disproves the reported condition; record why.

Risk acceptance and suppression are dispositions, not proof of false positive. Do not silently discard suppressed results.

## Prioritize and Report

Sort by:

1. Independently calibrated behavioral impact
2. Reachability/exposure and baseline state
3. Affected asset/tenant/data/release path
4. Tool severity and code-flow evidence
5. Reviewer confidence

For every important result, include the original report signal and independently verified evidence. Report counts only after deduplication rules, scope, and suppression treatment are clear.

If using `scripts/summarize_sarif.py`, treat its output as normalization only. It does not verify source, exploitability, severity, or correctness.
