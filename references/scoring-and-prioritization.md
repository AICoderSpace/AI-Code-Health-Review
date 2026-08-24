# Scoring and Prioritization

Read this reference only when the user requests a score, grade, risk band, or refactor priority.

## Numeric Score Policy

Do not invent a numeric score. Report a number only when:

1. A named tool/report produced it, or the user supplied an explicit scoring model.
2. The analyzed scope, exclusions, tool/model version, configuration, and scale meaning are known.
3. The score remains attributed to that source and is not presented as independent truth.

Do not average unrelated security, correctness, test, and maintainability dimensions into a project score unless the supplied model explicitly defines that calculation. Do not convert qualitative judgment into a percentage.

If the user asks for a score without a model, provide a scoped qualitative risk band and explain the strongest evidence. If the user explicitly asks to design a rubric, disclose every dimension, weight, formula, assumption, and uncertainty before using it.

## Qualitative Bands

- **Critical risk**: credible severe compromise, destructive data failure, systemic outage, or equivalent core failure requiring immediate action.
- **High risk**: important-path behavioral or release risk requiring prompt correction.
- **Medium risk**: localized risk or meaningful change debt that should be planned and verified.
- **Low risk**: limited cleanup or polish with little behavioral impact.
- **Insufficient evidence**: the scope or runtime context cannot support a reliable band.

Attach every band to its scope. A healthy overall area can contain a high-risk hotspot.

## Priority Ordering

Order findings using judgment, not a hidden formula:

1. Impact on users, security boundaries, sensitive data, integrity, availability, or release trust
2. Credible reachability/likelihood and current exposure
3. Reversibility, blast radius, and availability of mitigation or rollback
4. Whether the issue is new/changed and lies on a critical/shared path
5. Evidence confidence
6. Cost and dependency order of the smallest safe remediation

Use tool severity and maintainability metrics only after this behavioral calibration.

## Refactor Priority

Prefer this sequence:

1. Authorization, security, privacy, destructive-action, and supply-chain boundaries
2. Data correctness, migrations, and data-loss prevention
3. Production stability, error handling, rollback, and resource release
4. Concurrency, async ordering, idempotency, and cancellation
5. Untested core business rules and high-change shared paths
6. Mixed responsibilities and repeated business rules
7. API/module ownership and coupling
8. Evidence-backed performance work
9. Documentation needed to use or change risky behavior safely
10. Naming, comments, formatting, and directory polish

## Risk Disposition

Use one disposition when governance context exists:

- **Reduce**: fix or add a control.
- **Avoid**: do not ship or remove the risky change.
- **Accept**: document rationale, compensating controls, owner, and review/expiry date.
- **Defer**: record why it is safe to postpone and what signal should trigger reassessment.

Do not silently convert an unresolved finding into accepted risk. Acceptance is an owner decision, not a reviewer assumption.

## Safe Deferrals

Usually defer low-risk style/naming issues outside changed code, intentional duplication with different business meaning, architecture changes without migration safety, and performance work without evidence. Never use deferment to hide a confirmed security, data-loss, or reliability blocker.
