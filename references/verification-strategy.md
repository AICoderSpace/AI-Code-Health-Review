# Verification Strategy

Use this reference to judge existing tests and to select verification for a finding or fix. Apply `execution-safety.md` before running project-controlled commands.

## Select and Stop

Choose checks that can confirm the identified failure, protect affected contracts, or meet the project's requirements. A review of one function does not automatically need the full suite; a shared contract or high-risk change may justify it.

Once the relevant checks pass, broaden or repeat them only for new changes, failures, or unresolved concerns. Do not add tests that merely restate a reversible, low-impact edit. Verify UI and runtime claims at the corresponding layer; compilation and static inspection cannot establish live behavior.

Keep results scoped to the actual fixture and environment. Use isolated synthetic data, with no production history, metadata, credentials, or uncontrolled network dependency.

## Review the Tests, Not Just Their Presence

Ask:

- Would the test fail if the target behavior were broken?
- Does it assert outcomes and side effects rather than implementation trivia?
- Does it cover negative, boundary, failure, and recovery paths proportional to risk?
- Are mocks/fakes faithful to the contract and failure behavior of the real dependency?
- Is the test deterministic, isolated, and maintainable?
- Does it exercise the correct layer: unit, integration, contract, end-to-end, or artifact/runtime check?
- Can concurrency, time, randomness, locale, filesystem, environment, and network assumptions be controlled?

Coverage is a locator, not proof. A high percentage can miss the only dangerous branch.

## Verification by Risk

| Risk | Useful verification |
|---|---|
| Correctness | focused unit/integration tests, boundary tables, reference examples, property-based invariants |
| Authorization/security | negative and cross-role/tenant tests, source-to-sink checks, abuse cases, safe fuzzing of parsers/inputs |
| Privacy/sensitive data | redaction/log checks, access/export/delete tests, telemetry/config inspection |
| Data integrity/migration | transaction failure tests, idempotency/replay, mixed-version compatibility, dry-run/backfill checks, rollback rehearsal |
| Reliability | timeout/cancellation, dependency failure, retry bounds, partial failure, restart/recovery, cleanup assertions |
| Concurrency | deterministic scheduler where available, race detector, stress/repetition, stale-response and duplicate-submit tests |
| Resource management | leak/handle checks, bounded cache/queue tests, cancellation cleanup, temporary-file cleanup |
| Supply chain/release | lockfile consistency, provenance/attestation verification, signature/checksum checks, reproducible-build evidence, CI permission review |
| Artifact resilience | exact Release hash, signing/entitlement and dependency audit, format-appropriate compiler/linker mitigation checks with applicability states, symbol/debug/secret exposure checks, source-to-artifact provenance, isolated static/dynamic abuse cases |
| Performance | representative benchmark, profiler/trace, load/capacity test, query plan, memory/allocation measurement |

Do not run offensive tests against live or third-party systems. Use isolated fixtures, local targets, or explicit authorization and scope.

## Fix Verification

Prefer a regression test that fails before the fix and passes after it when feasible. Also check:

1. The original failure path is closed.
2. Existing intended behavior remains intact.
3. Alternate entry points and error paths do not bypass the fix.
4. New cleanup, rollback, permission, or migration behavior is covered.
5. Public contracts and documentation remain accurate.

For refactors, characterize behavior before changing structure. For untested legacy code, add focused characterization tests around the risky boundary rather than asserting every incidental detail.

## When Verification Cannot Run

Do not substitute confidence language for execution. State:

- What was inspected statically
- What command/check should run
- Why it was not run: unavailable tool, unsafe entry point, missing dependency, authorization, time/resource limit, or absent environment
- Which conclusion remains uncertain as a result

Do not recommend installing dependencies or uploading source merely to eliminate a low-value uncertainty.

## Verification Record

```md
Verification run:
- `<command or check>` — result/exit status, tool version/config, target/revision

Not run:
- `<check>` — reason and residual uncertainty

Side effects/cleanup:
- ...
```
