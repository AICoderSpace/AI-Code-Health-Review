# Maintainability Risk Mapping

Use this reference for broad project reviews, code-health checks, and refactor prioritization. Metrics locate candidates; inspected behavior determines findings.

## Contents

- Worst-first mapping
- Evidence hierarchy
- Maintainability signals
- False-positive controls
- Risk-map templates

## Worst-First Mapping

Do not average away hotspots. Rank targets using available evidence:

1. Confirmed correctness, security, data, reliability, concurrency, or release risk
2. Exposure and failure impact: public/auth/data/destructive/critical paths first
3. Change surface: changed contracts, migrations, dependencies, CI/CD, infrastructure, and shared modules
4. Structural signals: complexity, duplication, size, coupling, weak error handling, and poor test protection
5. Churn and centrality only when repository history or tooling actually provides them

Deep-review the highest-risk few targets before making project-level claims. For PRs, still account for every changed file and line in scope.

## Evidence Hierarchy

- **Strong**: directly observed incorrect behavior/path, failing test, reproducible result, unsafe configuration, or verified source-to-sink flow.
- **Moderate**: code path with credible preconditions but unverified runtime context; missing tests around a high-impact boundary.
- **Weak**: size, complexity, naming, or analyzer score without a concrete behavioral consequence.

Use weak signals to choose where to inspect, not to inflate severity.

## Maintainability Signals

### Complexity

Look for decisions, state transitions, validation, transformation, side effects, and recovery interleaved in one unit. Prefer guard clauses, named predicates, explicit phases, or a state machine only when those changes clarify real behavior.

### Duplication

Look for repeated business rules, authorization conditions, query construction, failure handling, and state transitions. Extract only genuinely shared meaning; similar-looking code with different domain ownership may be safer left separate.

### Size and Responsibility

Treat size as a prompt to ask whether ownership is mixed. A long cohesive parser may be safer than a short function that combines permission checks, writes, external calls, and cleanup.

### Coupling and Structure

Look for circular dependencies, broad public APIs, unrelated imports, cross-layer knowledge, utility dumping grounds, hidden globals, and changes requiring unrelated modules to move together.

### Error and Resource Handling

Inspect I/O, network, database, parsing, process, SDK, transaction, stream, subscription, timer, and temporary-file paths. Look for swallowed errors, unbounded retries, partial updates, asymmetric cleanup, or failure types callers cannot distinguish.

### Test Protection

Look for core behavior trapped in UI/event handlers, hard-coded time/random/network/environment dependencies, tests coupled to implementation details, and important failure paths without meaningful assertions. Read `verification-strategy.md` for test-quality checks.

### Documentation and Naming

Prioritize public contracts, compatibility constraints, security assumptions, and risky workarounds. Treat names and comments as findings only when they can cause misuse or materially increase change risk.

## False-Positive Controls

- Prefer project and tool configuration over generic expectations.
- Do not score generated/vendor code for maintainability unless the user owns and changes it.
- Recognize framework lifecycle and declarative patterns before labeling them over-engineered.
- Do not demand abstraction for intentional duplication with separate business meaning.
- Do not recommend performance work without runtime evidence or a credible unbounded path.
- Do not recommend directory reshuffles that leave ownership and behavior unchanged.

## Manual Risk Map

```md
| Target | Risk band | Evidence strength | Main signals | First review question |
|---|---|---|---|---|
| `src/foo.ts` | High | Moderate | public write path, mixed rollback, weak tests | Can a failed request leave state partially committed? |
```

## Machine Report Risk Map

Use `machine-report-protocol.md` first.

```md
| Target | Tool/rule | Baseline | Tool severity | Verified status | First safe step |
|---|---|---|---|---|---|
| `src/foo.ts` | `tool/rule-id` | new | error | Confirmed | isolate write from validation and test rollback |
```

For weighted code-health reports, first preserve coverage state, skipped/failed files, parser mode, configuration, exclusions, weights, per-file signals, and actual location metadata. A project score with empty, partial, fallback, or unknown coverage cannot establish project health. If using `scripts/summarize_code_health.py`, use its worst-first file order only to select review targets.

## Recommendation Quality Bar

Anchor every recommendation to a location or explicit pattern, explain the behavioral or change risk, propose the smallest useful action, and pair it with verification. Avoid empty advice such as "improve structure" or "optimize this."
