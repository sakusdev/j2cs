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
prompts/         Worker and reviewer instructions for parallel generation
.github/         CI
```

## Translation tiers

- `native` — maps cleanly to normal C#/.NET semantics.
- `helper` — compiles to C# but requires a small compatibility helper.
- `runtime` — requires dynamic JavaScript-compatible behavior at runtime.
- `unsupported` — cannot currently be translated safely.

## Example

`Array.prototype.push` cannot simply become `List<T>.Add`: JavaScript `push()` returns the new length, while `Add()` returns `void`. Rules in j2cs record this semantic difference explicitly and test it.

## Parallel workflow

1. Pick one narrow domain (Array, String, Promise, coercion, Node fs, Electron IPC, etc.).
2. Create a branch such as `rules/array-core`.
3. Add or update rules conforming to `schema/rule.schema.json`.
4. Add tests for normal and edge behavior.
5. Open a PR.
6. A separate reviewer should verify JavaScript semantics, C# validity, conflicts with existing rules, and fallback decisions.

The repository is intentionally a knowledge base first. A compiler can consume this data later through an AST/type-analysis pipeline.
