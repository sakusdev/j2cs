# Coverage Gap Analyzer

`tools/coverage_gap.py` scans every rule under `rules/**` and compares the
measured corpus against `coverage/catalog.json`.

It ranks workstreams using:

- zero/low rule coverage,
- missing semantic sub-surfaces,
- runtime-heavy coverage,
- low/medium-confidence concentration,
- explicit project priority.

The analyzer does **not** claim that a rule-count target is a language-standard
coverage percentage. The catalog is a planning target used to find likely
holes in the knowledge base.

## Local usage

```bash
python tools/coverage_gap.py --top 20
python tools/coverage_gap.py \
  --json-out /tmp/coverage.json \
  --markdown-out /tmp/coverage.md \
  --issues-out /tmp/issues.json
```

Issue creation is dry-run by default:

```bash
python tools/create_gap_issues.py --top 10
```

With `GITHUB_TOKEN` and `GITHUB_REPOSITORY`, `--apply` creates READY
workstream issues. Existing open issues with the same `WORKSTREAM:` value are
deduplicated.

The `Coverage gaps` GitHub Actions workflow always produces a report artifact.
Its manual `workflow_dispatch` can additionally create the highest-ranked
READY issues.
