# Execution Safety

Apply this check before project-controlled code, builds, tests, linters, scanners, benchmarks, binaries, containers, package managers, or migrations, and before actions whose side effects or disclosure are unclear. Known read-only inspection and authorized text edits do not need a separate gate.

## Classify the Action

- **Read-only inspection**: file listing, text search, diff, metadata, parsing a known data file with trusted tooling.
- **Repository-controlled execution**: package scripts, Make/Task targets, test runners with project plugins, compiler/build hooks, local binaries, code generators, migrations, containers.
- **Environment-changing action**: dependency installation, package lifecycle scripts, service startup, cache/toolchain mutation, writes outside the workspace.
- **External disclosure**: cloud scanner, telemetry, artifact/report upload, remote API, paste service.
- **Destructive or production-affecting action**: data changes, deployment, credential use, external messages, irreversible commands.

Read-only inspection is the default. Other actions require understood side effects, authorization that covers the action, and bounded execution.

## Use Existing Authorization

The safety check is an assessment, not an automatic request for permission. Use authorization already supplied for the current task; do not ask again for the same scope. A local edit or test does not authorize publishing, external disclosure, production access, or other unrelated state changes.

If an action needs additional permission, identify its exact target and side effects, explain why existing authorization is insufficient, and prepare the authorized work before asking. Continue independent work while the action is blocked. If this reference is the reason for stopping, cite the specific requirement instead of invoking an unspecified safety gate.

## Inspect Before Running

Read the relevant entry points without executing them:

- `package.json` scripts and package-manager configuration
- Makefile, Taskfile, shell wrappers, build files, and test configuration
- Compiler, linter, formatter, coverage, and test plugins
- Pre/post-install, pre-commit, code-generation, and migration hooks
- Container entrypoints and compose/orchestration files
- CI/CD workflows and reusable third-party actions
- Scanner configuration, upload behavior, telemetry, and ignore/suppression files

Never assume a familiar command such as `npm test`, `make test`, or `pytest` is safe merely because of its name.

Reuse inspection from the current task while the relevant code, command, configuration, permissions, and data boundary remain unchanged. Reassess changed entry points and newly encountered side effects; do not reread unrelated configuration before each invocation.

## Safe Defaults

- Use the sandbox and least privilege available.
- Do not provide credentials, tokens, production configuration, signing keys, or personal data unless explicitly required and authorized.
- Use isolated synthetic stores, preferences, temporary paths, and other fixtures for verification. Authorization to review a project does not grant access to production data, real user history, or associated metadata and derivatives. Treat data of unknown origin as sensitive until its use is authorized.
- Keep network access disabled unless the task requires it and authorization permits it.
- Do not upload source, reports, symbols, or artifacts to third parties without explicit authorization.
- Do not install or update dependencies merely to make a review more complete. Explain the need and side effects first.
- Avoid package lifecycle scripts when a safe no-script inspection mode exists.
- Do not run repository binaries or generated executables before understanding their origin and purpose.
- Bound time, output, memory, input size, retries, concurrency, and generated artifacts when possible.
- Sanitize untrusted report/log text before terminal or Markdown rendering; do not emit active terminal controls, raw HTML, or unintended links.
- Keep writes inside the intended workspace and identify cleanup or rollback needs.
- Prefer existing lockfiles and toolchains; do not silently rewrite them.

## Secret Handling

If a credential or secret-like value is found:

1. Do not print, quote, copy, or place the value in a report.
2. Report the file/location and secret type with a redacted description only when necessary.
3. Avoid commands that echo environment variables, full configuration, headers, or process arguments containing secrets.
4. Recommend revocation/rotation only when exposure is credible; do not claim compromise without evidence.
5. Do not commit a redacted replacement unless the user asked for a fix and the project has a safe secret-management pattern.

## External Scanners

Determine whether a scanner is local-only or uploads code/metadata. Inspect configuration and documentation when available. A locally installed scanner can still execute project plugins, invoke builds, access the network, or read credentials.

Treat scanner output as unverified evidence. Record tool version, rules/profile, target, exclusions, and exit status. Never call a local pattern search an independent third-party SAST scan.

## Execution Record

For executed checks, report the following when material. Group commands that share a target and environment, and omit irrelevant or empty fields:

- Command or meaningful equivalent
- Working directory and target/revision
- Tool version and relevant config/profile when available
- Whether network, credentials, services, containers, or external uploads were involved
- Exit status and concise result
- Files or state materially changed
- Limitations, skipped checks, and cleanup/rollback status

If the gate cannot be satisfied safely, do not run the command. Continue with read-only analysis and state what remains unverified.

## Checklist

- [ ] Entry points and hooks inspected
- [ ] Side effects, network, credentials, and uploads understood
- [ ] Authorization matches the action
- [ ] Scope and resource use bounded
- [ ] Secret values protected
- [ ] Result and limitations recorded accurately
