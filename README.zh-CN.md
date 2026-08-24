# AI Code Health Review

[English](README.md)

一个面向 Codex 的证据驱动代码审查 skill，用于审查代码、diff、仓库、测试、依赖、CI/CD、基础设施配置、Release 产物以及机器生成的分析报告。

它关注真实工程风险，不把代码风格、扫描器输出或任意指标包装成虚假的确定性，并明确区分正确性、安全、隐私、数据完整性、可靠性、供应链完整性、测试质量、可维护性和性能。

## 核心能力

- 以发现为先的代码、PR、提交前和项目健康审查
- 面向认证、授权、敏感数据和不可信输入的威胁上下文审查
- 依赖、lockfile、CI/CD、容器、基础设施、provenance 和发布链路审查
- 基于威胁模型审查 Release 产物、签名、entitlements、敏感内容暴露和抗逆向韧性
- 在执行项目构建、测试、扫描器或包脚本前应用安全闸门
- 保留 baseline、fingerprint 和 suppression 的 SARIF 2.1.0 规范化
- 明确暴露空、部分、跳过、失败、配置、解析器和位置元数据限制的加权代码健康报告规范化
- 明确区分工具信号、已验证证据、严重度和置信度
- 不使用虚构项目分数或通用硬阈值的定性热点映射
- 基于风险审查测试质量并验证修复
- 提供小步、可验证的重构建议和剩余风险说明

## 不作出的承诺

这个 skill 不是 SAST/SCA 引擎、渗透测试、漏洞利用框架或合规认证，也不能证明软件不存在漏洞或无法被逆向。构建成功、测试通过、高分、空扫描报告、检测到调试器或应用了混淆都不等于安全。

仓库内容和分析报告会被视为不可信证据。在检查入口脚本和副作用之前，不执行项目控制的代码。

## 安装

在 Codex 中，优先使用内置安装器，让 Codex 选择其管理的用户级 skill 位置：

```text
$skill-installer 从 https://github.com/Marstlantis/AI-Code-Health-Review 安装仓库根目录的 skill，并命名为 ai-code-health-review
```

如需手动进行跨客户端用户级安装，请把仓库克隆到标准用户 skill 位置，并使用 skill 名称作为目标目录：

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Marstlantis/AI-Code-Health-Review.git "$HOME/.agents/skills/ai-code-health-review"
```

Codex 会自动检测 skill 变更；只有未显示时才需要重启。

项目级安装可放在：

```text
.agents/skills/ai-code-health-review/
```

## 使用示例

显式调用：

```text
$ai-code-health-review 审查这个 PR 的合并阻塞项和缺失测试
$ai-code-health-review 评估这个仓库的代码健康和重构优先级
$ai-code-health-review 验证这份 SARIF 报告中风险最高的发现
$ai-code-health-review 规范化这份代码健康 JSON，并验证最可信的高风险热点
$ai-code-health-review 审查依赖、CI/CD 和发布供应链风险
$ai-code-health-review 审查这个 macOS Release 产物的签名、entitlements、符号、敏感信息、依赖和抗逆向韧性
```

匹配代码审查场景时，也可以由 Codex 隐式调用。

## SARIF 规范化脚本

内置脚本只使用 Python 标准库读取 SARIF 2.1.0：

```bash
python3 scripts/summarize_sarif.py report.sarif --format markdown
python3 scripts/summarize_sarif.py report.sarif --format json
```

脚本保留 driver 与 extension rule component 元数据、规则名称与 rank、baseline 状态、原始 fingerprints、全部结果位置、suppression justification 和 code-flow 数量，并区分空 `runs` 数组与表示生产者填充失败的 `runs: null`。它只进行确定性的规范化和保守去重，不会验证源码行为、可达性、可利用性、严重度或正确性。输出会保留报告中的路径和消息，除非已获授权，否则应保持在本地。

解析器拒绝不受支持的 SARIF 版本、非标准 JSON 常量和超过 50 MiB 的报告。Markdown 输出会中和不可信报告字段中的终端控制符、双向文本控制符、原始 HTML 分隔符和可点击链接标记。

## 代码健康报告规范化脚本

仅使用标准库的代码健康规范化脚本可读取包含 `summary`、`files[].metrics` 和 `files[].parseResult` 字段的兼容加权逐文件 JSON 报告：

```bash
python3 scripts/summarize_code_health.py report.json --tool-name example-analyzer --format markdown
python3 scripts/summarize_code_health.py report.json --tool-name example-analyzer --format json
```

脚本保留明确归属的工具分数、严重度、指标、语言、文件数量和可选位置，同时区分 coverage 是 available、partial、empty、not populated 还是 unknown。即使工具报告 100 分，只要没有实际分析文件，仍属于无数据证据。缺失的权重、include/exclude 配置、解析器模式、失败计数或指标位置会保持不可用，不能据此做项目级分数结论。

脚本不会运行分析器、安装 npm 包、调用 MCP、上传源码、验证指标公式或判断必须重构；它只安全规范化用户提供的本地报告，供后续源码验证。输出会保留报告路径、项目路径、文件路径和指标详情，未经披露授权应保持在本地。

## 审查模型

重要发现包含：

- 严重度、状态和置信度
- 精确位置和实际检查过的证据
- 具体影响和最小安全修复
- 可以证明修复有效的验证方式
- 适用时的安全前置条件、可达性和受影响资产
- 机器报告的工具、规则、baseline、fingerprint 和 suppression 信息
- 仅在实际核对后给出的版本化标准映射

数字分数始终归属于生成它的工具或评分模型。没有明确模型时，只使用带审查范围的定性风险等级。

## 权威基线

skill 格式遵循 [OpenAI Build skills 指南](https://learn.chatgpt.com/docs/build-skills)和 [Agent Skills 规范](https://agentskills.io/specification)。审查指导使用以下版本化或由发布方维护的资料：

- [NIST SP 800-218，安全软件开发框架 1.1](https://csrc.nist.gov/pubs/sp/800/218/final)
- [OWASP 应用安全验证标准 5.0.0](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Code Review Guide v2](https://owasp.org/www-project-code-review-guide/)
- [SLSA 1.2，Approved](https://slsa.dev/spec/v1.2/)
- [OASIS SARIF 2.1.0 plus Errata 01](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [Google Engineering Practices：Code Review](https://google.github.io/eng-practices/review/reviewer/)
- [OpenSSF Scorecard](https://scorecard.dev/)

产物、二进制加固、指标和 Agent/MCP 审查还使用：

- [OWASP MASVS-RESILIENCE](https://mas.owasp.org/MASVS/11-MASVS-RESILIENCE/)和 [MASTG 抗逆向指导](https://mas.owasp.org/MASTG/0x05j-Testing-Resiliency-Against-Reverse-Engineering/)
- [MITRE CWE-656：依赖安全模糊化](https://cwe.mitre.org/data/definitions/656.html)
- [Apple Hardened Runtime](https://developer.apple.com/documentation/security/hardened-runtime)和 [macOS 分发签名指导](https://developer.apple.com/documentation/xcode/creating-distribution-signed-code-for-the-mac/)
- [OWASP Agentic Applications Top 10 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)和 [第三方 MCP Server 指南 1.0](https://genai.owasp.org/resource/cheatsheet-a-practical-guide-for-securely-using-third-party-mcp-servers-1-0/)
- [Microsoft BinSkim 规则](https://github.com/microsoft/binskim/blob/main/docs/BinSkimRules.md)、[Red Hat Annobin/annocheck](https://docs.redhat.com/en/documentation/red_hat_developer_toolset/10/html/user_guide/chap-annobin)、[SonarSource 指标定义](https://docs.sonarsource.com/sonarqube-server/user-guide/code-metrics/metrics-definition)和 [Mandiant capa 局限](https://github.com/mandiant/capa#limitations)

适用范围和限制见 [references/standards-map.md](references/standards-map.md)。涉及当前合规或最新指导时，应重新核对官方来源。

## 仓库结构

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

`SKILL.md` 保存精简的运行工作流，references 仅在相关场景下加载。两个 README 是开源仓库文档，不属于运行时提示词。

## 验证

只有内置脚本和测试需要 Python 3.10 或更高版本；skill 指令本身没有运行时包依赖。

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_package.py .
```

发布包验证器会拒绝常见系统杂物、压缩包、Python 缓存、符号链接、缺失文件、断开的直接引用和缺失的双语跳转。它会忽略顶层 Git checkout 元数据，因此可直接在正常 clone 中运行而不会扫描 `.git` 内部。

GitHub Actions 会在 Python 3.10 和 3.14 上运行标准库单测与包验证器；工作流只使用仓库只读权限，并将 GitHub 官方 actions 固定到完整提交 SHA。

## 贡献

贡献应保持证据契约和渐进加载结构：

1. 保持 `SKILL.md` 精简，把详细流程放入直接链接的 reference。
2. 标准只使用官方或一手来源，并记录版本或状态变化。
3. 没有具名、版本化、可复现的模型时，不添加通用指标阈值或评分权重。
4. 确定性脚本必须有测试，并避免网络依赖。
5. 不削弱执行安全、密钥保护、范围披露或机器报告人工验证。
6. 提交前运行全部验证命令。

## 许可证

[MIT License](LICENSE)，copyright (c) 2026 Marstlantis。
