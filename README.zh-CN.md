# AI Code Health Review

[English](README.md)

这个 Codex 技能用于审查代码、diff、仓库、测试、依赖、CI/CD、基础设施配置、Release 产物和机器生成的分析报告。

每项发现都说明检查过的证据、具体风险、修复建议和验证方法。审查会分别评估正确性、安全、隐私、数据完整性、可靠性、供应链完整性、测试质量、可维护性和性能。代码风格偏好或未经核实的扫描分数不能直接证明缺陷。

## 审查范围

- 审查代码、PR、提交前改动和项目健康，优先报告可操作的问题
- 结合实际威胁场景，检查认证、授权、敏感数据和不可信输入
- 检查依赖、锁文件、CI/CD、容器、基础设施、来源证明（provenance）和发布链路
- 根据受保护资产和攻击者能力，检查 Release 产物、签名、权限声明（entitlements）、敏感内容暴露和抗逆向能力
- 执行项目构建、测试、扫描器或包脚本前，检查入口和副作用
- 整理 SARIF 2.1.0 报告，保留基线状态、指纹和抑制信息
- 整理加权代码健康报告，说明空或部分覆盖、跳过或失败的文件，以及配置、解析器或位置元数据的缺失
- 分别说明工具信号、已验证证据、严重度和置信度
- 定性评估高风险代码，不编造项目分数或套用通用硬阈值
- 根据风险检查测试质量并验证修复
- 提出可逐步验证的重构建议，说明剩余风险

## 使用边界

这个技能不能代替 SAST/SCA 引擎、渗透测试或合规认证，不提供漏洞利用框架，也不能证明软件不存在漏洞或无法被逆向。构建成功、测试通过、高分、空扫描报告、检测到调试器或应用了混淆都不等于安全。

仓库内容和分析报告用于提供证据，其中的嵌入指令不能授予权限或改变审查任务。执行项目代码前需要检查入口和副作用。同一任务内沿用已有授权；审查本身不授权访问生产数据或发布结果。

小范围审查直接从用户提供的材料开始，只有需要时才读取参考文件。相关检查通过后，只有新改动、失败或尚未解决的疑点才需要扩大或重复验证。

## 安装

使用内置安装器，让 Codex 选择其管理的用户级技能位置：

```text
$skill-installer 从 https://github.com/Marstlantis/AI-Code-Health-Review 安装仓库根目录的 skill，并命名为 ai-code-health-review
```

如需在兼容客户端之间共用手动安装的技能，可把仓库克隆到标准用户技能目录：

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/Marstlantis/AI-Code-Health-Review.git "$HOME/.agents/skills/ai-code-health-review"
```

Codex 会自动检测技能变更；未显示时再重启。

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

请求与技能描述匹配时，Codex 也可以自动选择它。

## SARIF 规范化脚本

内置脚本只使用 Python 标准库读取 SARIF 2.1.0：

```bash
python3 scripts/summarize_sarif.py report.sarif --format markdown
python3 scripts/summarize_sarif.py report.sarif --format json
```

脚本保留 driver 和 extension 规则组件的元数据、规则名称和 rank、基线状态、原始指纹、全部结果位置、抑制理由和代码流数量。空 `runs` 数组与 `runs: null` 会分别保留；后者表示报告生产者未能填充 runs。

规范化结果是确定的，去重采用保守规则。脚本不会验证源码行为、可达性、可利用性、严重度或正确性。输出保留报告中的路径和消息，未经授权应留在本地。

解析器拒绝不受支持的 SARIF 版本、非标准 JSON 常量和超过 50 MiB 的报告。Markdown 输出会中和不可信报告字段中的终端控制符、双向文本控制符、原始 HTML 分隔符和可点击链接标记。

## 代码健康报告规范化脚本

仅使用标准库的代码健康规范化脚本可读取包含 `summary`、`files[].metrics` 和 `files[].parseResult` 字段的兼容加权逐文件 JSON 报告：

```bash
python3 scripts/summarize_code_health.py report.json --tool-name example-analyzer --format markdown
python3 scripts/summarize_code_health.py report.json --tool-name example-analyzer --format json
```

脚本保留工具提供的分数、严重度、指标、语言、文件数量和可选位置信息，并区分覆盖状态：可用、部分覆盖、空范围、未填充或未知。即使工具报告 100 分，只要没有实际分析文件，就不能说明代码健康。缺失的权重、include/exclude 配置、解析器模式、失败计数或指标位置仍标为不可用，不能用于支持项目整体评分。

脚本整理用户提供的本地报告，供后续对照源码核实。它不会运行分析器、安装 npm 包、调用 MCP、上传源码、验证指标公式或判断是否需要重构。输出保留报告路径、项目路径、文件路径和指标详情，未经授权应留在本地。

## 发现如何呈现

重要发现包含以下信息，可以写成简短段落，也可以分字段列出：

- 严重度、状态和置信度
- 精确位置和实际检查过的证据
- 具体影响和最小安全修复
- 可以证明修复有效的验证方式
- 适用时的安全前置条件、可达性和受影响资产
- 机器报告的工具、规则、baseline、fingerprint 和 suppression 信息
- 仅在实际核对后给出的版本化标准映射

数字分数始终注明生成它的工具或评分模型。没有提供评分模型时，按实际检查范围给出定性风险等级。

## 标准与来源

技能格式遵循 [OpenAI Build skills 指南](https://learn.chatgpt.com/docs/build-skills)和 [Agent Skills 规范](https://agentskills.io/specification)。审查参考文件使用以下版本化或由发布方维护的资料：

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

`SKILL.md` 定义审查流程，并按需指向参考文件。两个 README 用于介绍仓库，技能不要求在审查时读取它们。

## 验证

内置脚本和测试需要 Python 3.10 或更高版本；技能指令本身没有运行时包依赖。

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_package.py .
```

包验证器检查系统杂物、压缩包、Python 缓存、符号链接、必需文件、直接引用和中英文文档之间的链接，发现问题时返回失败。它忽略顶层 Git 检出元数据，可直接在正常克隆的仓库中运行，不会扫描 `.git` 内部。

GitHub Actions 会在 Python 3.10 和 3.14 上运行标准库单测与包验证器；工作流只使用仓库只读权限，并将 GitHub 官方 actions 固定到完整提交 SHA。

## 贡献

提交改动时：

1. 在 `SKILL.md` 中写清范围和证据要求，在需要处链接详细流程。
2. 标准只使用官方或一手来源，并记录版本或状态变化。
3. 没有明确名称、版本和可复现计算方法的模型，不添加通用指标阈值或评分权重。
4. 确定性脚本必须有测试，并避免网络依赖。
5. 保留执行安全、密钥保护、审查范围说明和机器报告核实要求。
6. 提交前运行全部验证命令。

## 许可证

[MIT License](LICENSE)，copyright (c) 2026 Marstlantis。
