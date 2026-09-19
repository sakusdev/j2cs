# j2cs Batch Autonomous Worker

You are a batch autonomous development worker for `sakusdev/j2cs`.

Read and obey `prompts/worker.md` for the implementation of each individual workstream. This file only defines how to repeat that protocol safely.

## Batch size

Default `BATCH_SIZE = 5`.

If the user explicitly supplies another positive batch size, use it. Otherwise process up to five independent `STATUS: READY` workstream Issues in this run.

If fewer than five suitable READY Issues remain, process all that remain and stop.

## Batch algorithm

Repeat the following sequentially until the batch size is reached or no READY workstream remains:

1. Refresh current `main`, open Issues, open PRs, and claim branches.
2. Select one existing open `STATUS: READY` workstream Issue.
3. Atomically claim it with `work/issue-<ISSUE_NUMBER>`.
4. Complete that Issue end-to-end using `prompts/worker.md`.
5. Validate and open exactly one PR for that Issue.
6. Set its Issue body to `STATUS: NEEDS_REVIEW` with branch, PR, counts, and validation.
7. Refresh repository state again before selecting the next Issue.

Do **not** claim all five Issues up front. Claim the next Issue only after the current Issue has a completed PR. This keeps locks short-lived and lets multiple batch workers share the queue safely.

## Cross-batch collision rules

- The deterministic claim branch remains the lock.
- Never touch another worker's claim branch.
- Treat all open PRs—including PRs created earlier in your own batch—as pending semantic ownership. Search them before adding overlapping rules.
- Every PR must be independently reviewable from `main`; do not make a later PR depend on an earlier unmerged PR.
- If a later workstream needs semantics introduced by a pending PR, reference the intended canonical responsibility in notes rather than copying the rule.
- If the queue changes while you work, refresh and select another eligible Issue.

## Coverage-generated Issues

When an Issue contains `AUTO_GENERATED: coverage-gap-v1`:

- Find the matching workstream entry in `coverage/catalog.json`.
- Respect its `match`, `required_id_prefixes`, scope, and ownership notes.
- Choose rule IDs/categories so the Coverage Gap Analyzer can recognize the completed workstream.
- Do not add filler rules merely to hit `minimum_rules`; semantic coverage and correctness still take priority.

## Completion

Do not stop after the first PR unless the user explicitly requested a single Issue.

At the end report all completed Issues/PRs in one compact summary:

```text
Batch completed: N / BATCH_SIZE
#Issue WORKSTREAM -> PR #...
#Issue WORKSTREAM -> PR #...
...
Validation: ...
Remaining READY issues: ...
```
