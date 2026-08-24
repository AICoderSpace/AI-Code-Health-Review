# Metric and Language Calibration

Use this reference when a tool reports numeric metrics or the user asks whether code is too complex, too large, or poorly structured.

## Calibration Precedence

Use evidence in this order:

1. Project-enforced configuration and quality gates
2. The actual analyzer's documented metric, version, configuration, and output
3. Established repository conventions supported by healthy neighboring code
4. Qualitative change-risk analysis when no authoritative threshold exists

Do not invent a universal threshold, translate one tool's metric into another, or present a language-specific number without a named source and version. Cyclomatic complexity, cognitive complexity, nesting, line counts, and parameter counts measure different things and are not interchangeable.

Metric names are not sufficient identity. Analyzer implementations may count language constructs differently, and quality gates combine metric keys, operators, thresholds, scope, and mode. Do not label an approximation from one analyzer as another analyzer's cognitive complexity, duplication density, coverage, rating, or gate result.

## Analyzer Coverage and Parser Mode

Before interpreting a metric, confirm that the analyzer actually parsed the language and file type, whether it used a full AST or a regex/generic fallback, which files failed or exceeded limits, and whether exact locations were exported. A language being listed as “supported” does not prove every syntax feature or generated form was parsed correctly.

Treat empty or partial coverage, silent fallback, missing configuration, and missing location metadata as report-completeness limitations. Do not allow a default or weighted score to hide those states.

## Qualitative Bands

- **Low concern**: control flow and ownership are easy to explain; failure paths are explicit; tests cover important branches.
- **Review needed**: several responsibilities or branches interact; behavior is understandable only with substantial context; tests leave meaningful paths uncertain.
- **High change risk**: mixed side effects and decisions, hidden state transitions, difficult failure recovery, or a small change requires reasoning across many paths.

A metric breach is a locator, not a finding. Report the concrete risk it reveals: untested branches, ambiguous ownership, duplicated rules, hidden side effects, unsafe cleanup, or costly change propagation.

## Language-Aware Questions

| Context | Questions that matter more than line count |
|---|---|
| JavaScript/TypeScript | Are async results ordered or cancelled? Are runtime validation and type assumptions aligned? Is UI state restored after failure? |
| Python | Are dynamic input boundaries validated? Are exceptions narrowed? Are context managers and cleanup paths complete? |
| Go | Are errors preserved and handled? Can goroutines, channels, timers, or contexts leak or outlive ownership? |
| Java/C# | Are framework lifecycle, dependency injection, transactions, nullability, and async boundaries explicit? |
| C/C++ | Are ownership, lifetime, bounds, integer behavior, cleanup, and undefined behavior controlled? |
| Rust | Is `unsafe` justified and contained? Are ownership escape hatches, panics, async cancellation, and blocking work understood? |
| Swift | Are actor/main-thread boundaries, cancellation, optionals, resource lifetime, and UI state transitions safe? |
| Shell | Are quoting, word splitting, globbing, pipeline failures, temporary files, and untrusted arguments controlled? |
| PHP/Ruby | Are framework magic, mass assignment, dynamic dispatch, serialization, and authorization boundaries visible and tested? |

Generated code, declarative configuration, framework glue, parsers, state machines, migrations, and performance-critical loops require domain-aware judgment. Do not penalize them mechanically for size or branching.

## Reporting Numeric Output

When a tool provides a number, attach it to the tool and scope:

```text
Tool signal: cognitive complexity 24 from <tool/version/config> for `foo`; independently verified risk: validation, persistence, and rollback are coupled across untested branches.
```

Do not convert that number into an independent project score or severity.
