# Standards and Primary Guidance Map

Use this reference only when the review needs formal security, supply-chain, artifact, machine-report, or code-review guidance. Standards guide coverage; inspected evidence supports findings.

Use the following versioned standards and publisher-maintained primary guidance. Recheck living sources before current-status or compliance claims.

| Source | Baseline | Use in this skill | Limits |
|---|---|---|---|
| [NIST SP 800-218, SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) | Version 1.1, Final | Secure-development outcomes, secure environments, component integrity, provenance, vulnerability response | Outcome framework; not a finding catalog or certification result; verify whether a newer final publication applies |
| [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) | Version 5.0.0 | Versioned technical security requirements for applicable web applications | Does not automatically apply to every application or prove deployment/runtime compliance |
| [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/) | Version 2 | Risk-based secure review, threat context, manual verification, review process | Guidance requires project/business context and reviewer judgment |
| [SLSA](https://slsa.dev/spec/v1.2/) | Version 1.2, Approved | Source/build integrity, provenance, attestations, verification, supply-chain threats | Does not cover every dependency or runtime security risk |
| [OASIS SARIF](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) | Version 2.1.0 plus Errata 01 | Tool/rule metadata, locations, code flows, fingerprints, suppressions, baseline state | Interchange format; does not validate analyzer accuracy |
| [Google Engineering Practices: Code Review](https://google.github.io/eng-practices/review/reviewer/) | Living guidance | Change context, test review, comment clarity, continuous code-health judgment | Organization-specific guidance, not a security/compliance standard |
| [OpenSSF Scorecard](https://scorecard.dev/) | Living project | Optional repository/security-practice signals for open-source projects | Scores and checks can change; they are signals to verify, not proof of project safety |
| [OWASP MASVS-RESILIENCE](https://mas.owasp.org/MASVS/11-MASVS-RESILIENCE/) and [MASTG anti-reversing guidance](https://mas.owasp.org/MASTG/0x05j-Testing-Resiliency-Against-Reverse-Engineering/) | Living guidance | Threat-driven client resilience, obfuscation, anti-debugging, anti-tamper, runtime protection, and testing limits | Missing resilience is not automatically a vulnerability; no client control is 100% effective |
| [MITRE CWE-656](https://cwe.mitre.org/data/definitions/656.html) | CWE-656 | Identify primary reliance on security through obscurity | Obscurity may add defense-in-depth cost but cannot replace sound security design |
| [Apple Hardened Runtime](https://developer.apple.com/documentation/security/hardened-runtime) and [macOS distribution signing](https://developer.apple.com/documentation/xcode/creating-distribution-signed-code-for-the-mac/) | Living Apple guidance | macOS runtime integrity, signing, entitlements, notarization, and nested-code review | Integrity and publisher identity controls do not prove confidentiality or reverse-engineering resistance |
| [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | 2026 public release | Goal hijack, tool misuse, identity/privilege, agentic supply chain, unexpected code execution, memory/context poisoning | Prioritization framework; not proof that a particular skill, agent, or MCP is vulnerable |
| [OWASP Third-Party MCP Server Guide 1.0](https://genai.owasp.org/resource/cheatsheet-a-practical-guide-for-securely-using-third-party-mcp-servers-1-0/) | Version 1.0 | Third-party MCP authentication, authorization, sandboxing, discovery, governance, least privilege, and human oversight | Guidance must be applied to the actual host, server, tools, data, and delegated permissions |
| [Microsoft BinSkim rules](https://github.com/microsoft/binskim/blob/main/docs/BinSkimRules.md) | Living open-source rule documentation | PE and ELF compiler/linker mitigations, signing, toolchain metadata, applicability states, and SARIF output | Tool results depend on binary format, architecture, policy, version, options, and available metadata; Pass and NotApplicable are not proof of safety |
| [Red Hat Annobin/annocheck](https://docs.redhat.com/en/documentation/red_hat_developer_toolset/10/html/user_guide/chap-annobin) | Publisher-maintained guidance | ELF compiler provenance notes and security-hardening checks | Distribution and toolchain specific; absence of notes may limit evidence rather than prove missing mitigation |
| [SonarSource metric definitions](https://docs.sonarsource.com/sonarqube-server/user-guide/code-metrics/metrics-definition) | Living product documentation | Tool-specific metric keys, language-sensitive complexity, duplication, size, coverage, and quality-gate interpretation | Definitions and gates are analyzer/version/configuration specific and cannot be translated into universal thresholds |
| [Mandiant capa](https://github.com/mandiant/capa#limitations) | Living open-source documentation | Static or dynamic executable-capability signals and packed-sample limitations | Capability matches do not establish maliciousness; packed or obfuscated static results may be misleading or incomplete |

## Mapping Rules

1. Check whether the source is applicable to the system and requested scope.
2. Open the current official publisher page when the user asks for latest/current guidance or a compliance claim; record the checked date and distinguish final/approved material from drafts and living guidance.
3. Include a versioned requirement ID when the standard supports it. For ASVS, prefer forms such as `v5.0.0-1.2.5`.
4. Map only requirements actually evaluated. Do not list standards decoratively.
5. Keep external mapping separate from finding evidence, severity, and confidence.
6. State controls, deployment, organization, or runtime areas that code review could not verify.
7. Never claim certification, full compliance, exploitability, or absence of vulnerabilities from this skill alone.

## Living-Source Use

- Use official publisher pages, primary specifications, or authoritative project documentation.
- Record the checked date and version/status in the review output when current guidance or compliance matters.
- Review changed terminology and requirement identifiers before mapping them.
- Do not reinterpret an old report under a new ruleset, metric definition, policy, or tool version without an explicit migration.
