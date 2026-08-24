# Report Templates

Use findings-first output and the smallest template that fits the reviewed scope.

## Contents

- Finding fields
- Minimal review
- PR review
- Pre-commit review
- Project health review
- Security/supply-chain review
- Release-artifact resilience review
- Machine report review
- Direct edit summary

## Finding Fields

Use these fields for important findings:

```md
1. [Severity] Category — title
   - Status: Confirmed / Potential / Needs information
   - Confidence: High / Medium / Low
   - Location:
   - Evidence:
   - Impact:
   - Fix:
   - Verification:
```

Add only applicable context:

```md
   - Preconditions/reachability:
   - Affected asset/data/tenant/artifact:
   - Existing mitigations:
   - Tool signal: tool/version/rule/baseline/fingerprint/suppression
   - Standard mapping: versioned requirement and applicability
   - Disposition: reduce / avoid / accept / defer, with governance details when supplied
```

## Minimal Review

```md
## Findings

1. [Severity] Category — title
   - Status:
   - Confidence:
   - Location:
   - Evidence:
   - Impact:
   - Fix:
   - Verification:

## Scope

Reviewed:
- ...

Not reviewed:
- ...

## Residual Risk

- ...
```

When there are no findings, say: "No significant issues found in the reviewed scope." Then list scope, uninspected areas, verification not run, and residual risk.

## PR Review

```md
## Blocking Findings

1. [Severity] Category — title
   - Status/Confidence:
   - Location:
   - Evidence:
   - Impact:
   - Fix:
   - Verification:

## Non-Blocking Suggestions

- ...

## Test Review

- Existing tests inspected:
- Would they fail on the identified regression?:
- Missing failure/boundary/abuse cases:
- Verification run/not run:

## Scope

- Target/revision:
- Changed files/lines accounted for:
- Context inspected:
- Exclusions:

## Merge Recommendation

Approve / Approve after minor changes / Request changes / Do not merge yet
```

## Pre-Commit Review

```md
## Submit Recommendation

Safe to submit / Submit after fixes / Do not submit yet

## Must Fix

- ...

## Should Fix Soon

- ...

## Safe To Defer

- ...

## Verification

- Run:
- Not run:
- Side effects/cleanup:
```

## Project Health Review

```md
## Highest-Risk Findings

1. [Severity] Category — title
   - Status/Confidence:
   - Location:
   - Evidence:
   - Impact:
   - Fix:
   - Verification:

## Risk Map

| Target | Risk band | Evidence strength | Main signals | First safe step |
|---|---|---|---|---|
| `path/or/module` | High/Medium/Low | Strong/Moderate/Weak | ... | ... |

## Scope

- Target/revision:
- Reviewed:
- Not reviewed:
- Verification run/not run:

## Health Summary

- Correctness/product behavior:
- Security/privacy:
- Data/reliability/concurrency:
- Supply chain/build/release:
- Test quality:
- Maintainability/performance:

## Recommended Order

1. ...

## Safe To Defer

- ...
```

## Security/Supply-Chain Review

```md
## Threat Context

- Assets/sensitive data:
- Roles/tenants/actors:
- Entry points/trust boundaries:
- Deployment exposure:
- Existing controls:
- Unknowns:

## Findings

1. [Severity] Security — title
   - Status/Confidence:
   - Location:
   - Preconditions/reachability:
   - Affected asset/data/tenant/artifact:
   - Evidence and path:
   - Existing mitigations:
   - Impact:
   - Fix:
   - Negative/abuse verification:
   - Standard mapping, if evaluated:

## Supply-Chain Scope

- Manifests/lockfiles:
- CI/CD/build/container/IaC:
- Provenance/signing/SBOM:
- Not verified:
```

## Machine Report Review

```md
## Verified Findings

1. [Severity] Category — title
   - Status/Confidence:
   - Location:
   - Tool signal: tool/version/rule/severity
   - Baseline/fingerprint/suppression:
   - Verified evidence:
   - Impact:
   - Fix:
   - Verification:

## Report Metadata

- Report/format:
- Target/revision:
- Tool/version/config/profile:
- Paths/languages/exclusions:
- Baseline and suppression availability:
- Completeness/limitations:

## Triage Summary

| Status | Count | Notes |
|---|---:|---|
| Confirmed | ... | ... |
| Potential | ... | ... |
| Needs information | ... | ... |
| False positive | ... | ... |

## Unverified or Suppressed Results

- ...

## Score Interpretation

- Original score and scope:
- What the score does not establish:
```

## Release-Artifact Resilience Review

```md
## Artifact Identity

- Distribution container/hash and component hashes:
- Platform/architecture/version:
- Release channel and signing/provenance:
- Claimed source/build relationship:
- Static/dynamic scope and tool versions:
- Binary-hardening policy and result/applicability states:

## Threat Context

- Protected assets:
- Attacker capability and entry points:
- Primary security controls:
- Resilience requirements and unknowns:

## Findings

1. [Severity] Artifact resilience — title
   - Status/Confidence:
   - Artifact component/location:
   - Preconditions and protected asset:
   - Static/dynamic evidence:
   - Existing controls:
   - Impact:
   - Fix:
   - Release-artifact verification:

## Coverage and Limits

- Binaries/resources inspected:
- Unsupported, skipped, or failed checks:
- Integrity versus confidentiality versus analysis-cost conclusion:
- Dynamic checks not run and why:
```

## Direct Edit Summary

```md
## What Changed

- ...

## Why

- Finding addressed:
- Behavior/contracts preserved:

## Verification

- Command/check and result:
- Tool version/config and target:
- Not run:
- Side effects/cleanup:

## Residual Risk

- ...
```

## Style

Explain the actual risk, not aesthetic dislike. Prefer: "Validation, persistence, and rollback are coupled; a failed write can leave partial state, and the failure branch is untested." Avoid: "This is not elegant" or "improve structure."
