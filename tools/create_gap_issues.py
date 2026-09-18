#!/usr/bin/env python3
"""Create READY workstream Issues from ranked coverage gaps.

Dry-run by default. Use --apply with GITHUB_TOKEN and GITHUB_REPOSITORY.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from coverage_gap import DEFAULT_CATALOG, analyze, issue_body, load_catalog, load_rules


def github_request(
    url: str, token: str, method: str = "GET", payload: dict | None = None
):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "j2cs-coverage-gap-analyzer",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def existing_workstreams(repo: str, token: str) -> set[str]:
    owner, name = repo.split("/", 1)
    page = 1
    found: set[str] = set()
    while True:
        url = (
            f"https://api.github.com/repos/{owner}/{name}/issues"
            f"?state=open&per_page=100&page={page}"
        )
        items = github_request(url, token)
        if not items:
            break
        for item in items:
            if "pull_request" in item:
                continue
            body = item.get("body") or ""
            for line in body.splitlines():
                if line.startswith("WORKSTREAM:"):
                    found.add(line.split(":", 1)[1].strip())
                    break
        if len(items) < 100:
            break
        page += 1
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--min-score", type=float, default=60.0)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    report = analyze(load_rules(), load_catalog(args.catalog))
    candidates = [
        item
        for item in report["workstreams"]
        if item["status"] != "covered" and item["score"] >= args.min_score
    ][: args.top]

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")

    if args.apply and (not repo or not token):
        print(
            "ERROR: --apply requires GITHUB_REPOSITORY and GITHUB_TOKEN",
            file=sys.stderr,
        )
        return 2

    existing = existing_workstreams(repo, token) if args.apply else set()
    created = 0

    for item in candidates:
        workstream = item["workstream"]
        title = f"WORKSTREAM: {workstream}"
        body = issue_body(item)

        if workstream in existing:
            print(f"SKIP existing open workstream: {workstream}")
            continue
        if not args.apply:
            print(
                f"DRY-RUN {title} score={item['score']} "
                f"status={item['status']}"
            )
            continue

        owner, name = repo.split("/", 1)
        url = f"https://api.github.com/repos/{owner}/{name}/issues"
        try:
            result = github_request(
                url, token, method="POST", payload={"title": title, "body": body}
            )
        except urllib.error.HTTPError as exc:
            print(
                f"ERROR creating {workstream}: HTTP {exc.code}",
                file=sys.stderr,
            )
            return 1

        print(
            f"CREATED #{result['number']} {workstream}: "
            f"{result['html_url']}"
        )
        existing.add(workstream)
        created += 1

    if args.apply:
        print(f"Created {created} issue(s).")
    else:
        print(f"Dry-run candidates: {len(candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
