# j2cs

A semantic rule database and differential-test corpus for translating JavaScript/TypeScript into C# while preserving JavaScript behavior as closely as possible.

The long-term goal is to support tooling that can remove as much of the JavaScript/Electron runtime as possible from existing Electron applications by compiling analyzable code to C# and falling back only when JavaScript semantics require it.

## Design principles

- **AST-first, never text replacement.** Rules describe semantics and lowering strategies, not regex rewrites.
- **Behavior over appearance.** A translation is valid only when observable behavior is preserved.
- **Native when safe, helpers when necessary, runtime fallback when unavoidable.**
- **Every rule needs tests.** Edge cases matter more than the happy path.
- **Parallel-friendly.** Contributors/AI workers should work on narrow rule families in separate branches and submit pull requests.

## Repository layout

```text
schema/          JSON Schema for rule files
rules/           Translation rules grouped by domain
tests/           Differential/behavior tests
prompts/         Autonomous worker/reviewer instructions
.github/         CI
```

## Translation tiers

- `native` — maps cleanly to normal C#/.NET semantics.
- `helper` — compiles to C# but requires a small compatibility helper.
- `runtime` — requires dynamic JavaScript-compatible behavior at runtime.
- `unsupported` — cannot currently be translated safely.

## Example

`Array.prototype.push` cannot simply become `List<T>.Add`: JavaScript `push()` returns the new length, while `Add()` returns `void`. Rules in j2cs record this semantic difference explicitly and test it.

## Autonomous parallel workflow

Rule-generation work is queued as GitHub Issues containing `WORKSTREAM:` and `STATUS: READY`.

An autonomous worker must read `prompts/worker.md`, select one ready issue, and atomically claim it by creating the deterministic branch:

```text
work/issue-<ISSUE_NUMBER>
```

That branch name is the concurrency lock. If it already exists, another worker owns the issue and the worker must choose another ready issue.

After claiming, the worker completes the workstream, validates all rules, opens a PR targeting `main` with `Closes #<ISSUE_NUMBER>`, and marks the issue ready for review. Workers must not merge their own PR unless explicitly instructed.

A new ChatGPT conversation therefore only needs a minimal launcher such as:

```text
sakusdev/j2cs の自律Workerとして prompts/worker.md に従い、未担当の READY Issue を1つ取得してPR作成まで完遂して。
```

Use `prompts/workstream-issue-template.md` when adding new workstream tasks.

## Coverage gap automation

`tools/coverage_gap.py` measures the current rule corpus against the planning
targets in `coverage/catalog.json`. It ranks missing, thin, and runtime-heavy
semantic workstreams and can emit machine-readable Issue proposals.

The `Coverage gaps` GitHub Actions workflow publishes a report artifact on
relevant changes. A manual workflow run can also create the highest-ranked
`STATUS: READY` Issues automatically; `tools/create_gap_issues.py` deduplicates
existing open workstreams before creation.

See `coverage/README.md` for usage and scoring details.

The repository is intentionally a knowledge base first. A compiler can consume this data later through an AST/type-analysis pipeline.
