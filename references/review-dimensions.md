# Review Dimensions

Use these dimensions for broad reviews and finding classification. Review only dimensions relevant to the scope, but do not let maintainability metrics outrank behavioral risk.

## Correctness and Product Behavior

Check requirements and user-visible behavior, boundary values, nullability, date/timezone and money handling, state transitions, compatibility, feature flags, and ambiguous return semantics. Verify documentation claims against implementation and tests.

## Security and Authorization

Check authentication, authorization at the real enforcement point, tenant isolation, injection, unsafe URLs/paths, SSRF, deserialization, secrets, cryptography, sensitive logging, resource abuse, and business-logic bypasses. For meaningful security scope, read `security-and-supply-chain.md` and establish threat context before severity.

## Privacy and Sensitive Data

Check collection minimization, consent/permission assumptions, retention/deletion, logging and telemetry, redaction, data export, cross-tenant exposure, and whether sensitive values cross unexpected trust boundaries. Do not claim legal compliance without the applicable jurisdiction and requirements.

## Data Integrity and Migration Safety

Check duplicate or partial writes, transaction boundaries, idempotency, lossy transforms, identifier consistency, timezone normalization, schema compatibility, backfill behavior, rollback/backout plans, and mixed-version deployment.

## Reliability and Error Handling

Check swallowed errors, uncaught async failures, retry/backoff limits, timeout/cancellation, circuit behavior, rollback/recovery, degraded dependencies, user-visible failure states, and whether failure leaves partial state.

## Concurrency and Async Order

Check stale or out-of-order responses, repeated submissions, shared mutable state, locks/transactions, task cancellation, goroutine/thread/actor ownership, cleanup of listeners/timers/subscriptions, and non-idempotent writes.

## Resource Management

Check file, database, network, stream, process, temporary-file, cache, memory, and subscription lifetime. Require symmetric success/failure cleanup and bounded growth.

## Supply Chain, Build, Release, and Artifact Resilience

Check dependency manifests and resolved lockfiles, install/lifecycle scripts, CI/CD workflows, pinned third-party actions, build inputs, code-generation steps, containers/base images, infrastructure configuration, artifact provenance, signing/checksums, SBOMs, and release permissions. When a shipped binary or client package is in scope, also check actual Release contents, debug metadata, symbols, secret-like material, entitlements/permissions, load paths, non-system dependencies, format-appropriate compiler/linker mitigations and applicability states, tamper controls, and threat-driven reverse-engineering resilience. Read `security-and-supply-chain.md` and, when applicable, `artifact-resilience-review.md`.

## API and Module Boundaries

Check ambiguous parameters/returns, boolean mode flags, hidden side effects, leaked internals, broad exports, circular dependencies, compatibility promises, ownership, and whether modules know too much about callers.

## Test Quality and Testability

Check whether important logic has explicit inputs/outputs, dependencies can be controlled safely, and tests would fail when behavior breaks. Review assertions, negative/failure cases, determinism, mock fidelity, and layer selection. Read `verification-strategy.md`.

## Maintainability

Check mixed responsibilities, repeated business rules, scattered state, change amplification, unclear ownership, deep decision flow, and dumping-ground modules. Length and complexity alone are not findings; explain the change risk.

## Performance and Capacity

Check unbounded input/loading/queues/caches, I/O in loops, N+1 access, missing pagination/backpressure, repeated computation, blocking work on async/UI threads, and hot-path copies. Without runtime evidence, classify bounded concerns as potential and recommend profiling or measurement.

## Readability, Documentation, and Style

Keep these below behavioral risks. Prefer precise names, comments explaining why/constraints, accurate public documentation, and repository-enforced style. Do not block on personal style preferences.
