# Workstream Issue Template

Use this format for autonomous j2cs rule-generation tasks.

```md
WORKSTREAM: <NAME>
STATUS: READY

## Scope
- ...
- ...

## Goals
- Add semantics-first rules for the scope above.
- Reuse existing canonical rules/helpers where appropriate.
- Avoid cross-workstream duplication.
- Include normal + semantic edge-case tests.

## Ownership notes
- List neighboring workstreams that may overlap.
- State which semantics should be reused rather than redefined.

## Completion
A worker must follow `prompts/worker.md`, claim via `work/issue-<ISSUE_NUMBER>`, validate, and open a PR containing `Closes #<ISSUE_NUMBER>`.
```

`STATUS: READY` means the issue may be claimed by an autonomous worker.

The deterministic branch name `work/issue-<N>` is the concurrency lock. If it already exists, another worker owns the task.
