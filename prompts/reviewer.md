# j2cs Rule Reviewer Prompt

Review a pull request that adds or changes j2cs translation rules.

Do not judge the PR by rule count. Judge semantic correctness.

For each rule, verify:

1. The described JavaScript behavior is correct for the stated preconditions.
2. The proposed C# lowering preserves observable behavior.
3. Return values, mutation, thrown exceptions, coercion, ordering, and edge cases are accounted for.
4. A `native` rule does not silently depend on JavaScript runtime semantics.
5. A `helper` rule clearly identifies the helper contract.
6. A `runtime` or `unsupported` decision is used when static/native translation would be unsafe.
7. Tests include at least one edge case where JavaScript and idiomatic C# differ.
8. The rule does not conflict with an existing rule or duplicate it under another ID.
9. The file conforms to `schema/rule.schema.json`.
10. Any reference or claim that is uncertain is flagged rather than guessed.

Common traps to look for:

- `Array.prototype.push()` returns the new length; `List<T>.Add()` returns void.
- JS `==` is not C# `==`.
- JS truthiness cannot generally become a C# boolean condition.
- `undefined` and `null` are distinct in JavaScript.
- JS numbers are IEEE-754 doubles by default; C# integer inference can change semantics.
- `NaN`, `-0`, overflow, and bitwise operators need care.
- property access can invoke getters, proxies, or prototype lookup.
- built-ins can be monkey-patched unless static analysis proves otherwise.
- Promise/microtask ordering is not identical to ordinary C# Task scheduling.

Prefer requesting a fallback tier over approving an unsound native translation.
