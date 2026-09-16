# j2cs Rule Worker Prompt

You are contributing translation rules to `sakusdev/j2cs`.

Work on exactly one narrow JavaScript/TypeScript domain assigned to you. Do not modify unrelated rule families.

For every construct/API you cover:

1. Determine the observable ECMAScript/Node/Electron behavior.
2. Identify semantic differences with idiomatic C#/.NET.
3. Decide the safest lowering tier: `native`, `helper`, `runtime`, or `unsupported`.
4. Prefer native C# only when behavior is preserved for the stated requirements.
5. If a compatibility helper is required, name it explicitly and describe what it must preserve.
6. If dynamic behavior prevents safe AOT translation, mark the rule `runtime` instead of forcing a lossy translation.
7. Add normal and edge-case tests.
8. Avoid regex/text-replacement assumptions; rules are consumed after AST/type/semantic analysis.
9. Keep rules small and composable.
10. Do not commit directly to `main`; use a dedicated branch and PR.

Pay special attention to:

- coercion and truthiness
- `undefined` vs `null`
- return values and mutation
- exceptions
- property lookup / prototype behavior
- `this` binding
- closures and scope
- async ordering / microtasks
- numeric edge cases (`NaN`, infinities, `-0`)
- heterogeneous arrays/objects
- overridden or monkey-patched built-ins

A rule that honestly chooses runtime fallback is better than an incorrect native rule.
