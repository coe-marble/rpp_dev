#!/usr/bin/env python3
"""Aggregate existing GitHub Actions results for the committed submodule pins."""

import argparse
import configparser
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class Submodule:
    path: str
    repository: str
    sha: str


@dataclass(frozen=True)
class Result:
    module: Submodule
    state: str
    detail: str
    url: str


def repository_from_url(url):
    if url.startswith("git@github.com:"):
        repository = url.removeprefix("git@github.com:")
    else:
        parsed = urlsplit(url)
        if parsed.hostname != "github.com" or parsed.scheme not in {"https", "ssh"}:
            raise ValueError(f"Unsupported GitHub submodule URL: {url}")
        repository = parsed.path.lstrip("/")
    repository = repository.removesuffix(".git")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise ValueError(f"Invalid GitHub repository: {repository}")
    return repository


def pinned_submodules(root):
    def git(*arguments):
        return subprocess.check_output(["git", "-C", str(root), *arguments], text=True)

    config = configparser.ConfigParser(interpolation=None)
    config.read_string(git("show", "HEAD:.gitmodules"))
    modules = []
    for section in config.sections():
        path = config[section]["path"]
        # Read the gitlink in HEAD, never the submodule worktree or branch tip.
        entries = git("ls-tree", "-z", "HEAD", "--", path).split("\0")
        matches = [entry.split("\t", 1)[0].split() for entry in entries
                   if entry and entry.split("\t", 1)[1] == path]
        if len(matches) != 1 or matches[0][:2] != ["160000", "commit"]:
            raise ValueError(f"Submodule {path} has no committed gitlink")
        modules.append(Submodule(path, repository_from_url(config[section]["url"]),
                                 matches[0][2]))
    if not modules:
        raise ValueError("No pinned submodules found; refusing to report success")
    return modules


class GitHub:
    def __init__(self, token):
        self.token = token

    def workflow_runs(self, module, workflow):
        runs = []
        page = 1
        while True:
            query = urlencode({"head_sha": module.sha, "per_page": 100, "page": page})
            url = (f"https://api.github.com/repos/{module.repository}/actions/workflows/"
                   f"{quote(workflow, safe='')}/runs?{query}")
            request = Request(url, headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "rpp-submodule-ci",
            })
            with urlopen(request, timeout=20) as response:
                payload = json.load(response)
            batch = payload["workflow_runs"]
            runs.extend(batch)
            if not batch or len(runs) >= payload["total_count"]:
                return runs
            page += 1


def inspect_module(module, workflow, fetch):
    workflow_url = f"https://github.com/{module.repository}/actions/workflows/{workflow}"
    try:
        runs = [run for run in fetch(module, workflow) if run.get("head_sha") == module.sha]
    except HTTPError as error:
        return Result(module, "error", (
            f"GitHub HTTP {error.code}: check RPP_CI_TOKEN access and workflow {workflow}"
        ), workflow_url)
    except (URLError, TimeoutError) as error:
        return Result(module, "error", f"GitHub temporarily unavailable ({type(error).__name__})",
                      workflow_url)
    if not runs:
        return Result(module, "pending", f"No {workflow} run for pinned commit", workflow_url)
    latest = max(runs, key=lambda run: (run["id"], run.get("run_attempt", 1)))
    url = latest.get("html_url", workflow_url)
    if latest["status"] != "completed":
        return Result(module, "pending", latest["status"], url)
    conclusion = latest.get("conclusion")
    return Result(module, "success" if conclusion == "success" else "failure",
                  conclusion or "completed without a conclusion", url)


def collect_results(modules, workflow, fetch):
    results = [inspect_module(module, workflow, fetch) for module in modules]
    for result in results:
        print(f"{result.module.path} {result.module.sha[:12]}: {result.state} — {result.detail}",
              flush=True)
    return results


def summary(results, workflow):
    lines = ["## Submodule CI", "",
             f"Required workflow: `{workflow}`. Results are for the commits pinned in this checkout.",
             "", "| Submodule | Pinned commit | Result | Details |",
             "| --- | --- | --- | --- |"]
    for result in results:
        module = result.module
        commit = f"https://github.com/{module.repository}/commit/{module.sha}"
        detail = result.detail.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{module.path}` | [{module.sha[:12]}]({commit}) | "
                     f"[{result.state}]({result.url}) | {detail} |")
    if any(result.state == "pending" for result in results):
        lines.extend(["", "Some CI results are missing or unfinished. "
                      "Rerun Submodule CI after the submodule workflows finish. "
                      "This job does not wait or poll."])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--workflow", default="ci.yml")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN")
    if not token:
        print("GH_TOKEN is required; configure the RPP_CI_TOKEN Actions secret.", file=sys.stderr)
        return 1
    try:
        modules = pinned_submodules(args.root)
        results = collect_results(modules, args.workflow, GitHub(token).workflow_runs)
        report = summary(results, args.workflow)
        print(report)
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as output:
                output.write(report)
        return 0 if all(result.state == "success" for result in results) else 1
    except (ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Unable to check submodule CI: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
