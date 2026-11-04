import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

from submodule_ci import (
    GitHub, Result, Submodule, inspect_module, pinned_submodules, repository_from_url,
    collect_results, main, summary,
)


MODULE = Submodule("src/example", "coe-marble/example", "a" * 40)


def run(run_id=1, status="completed", conclusion="success", sha=MODULE.sha, attempt=1):
    return {"id": run_id, "head_sha": sha, "status": status, "conclusion": conclusion,
            "run_attempt": attempt, "html_url": f"https://github.com/runs/{run_id}"}


class SubmoduleCITests(unittest.TestCase):
    def test_repository_urls(self):
        for url in ("git@github.com:coe-marble/example.git",
                    "https://github.com/coe-marble/example.git",
                    "ssh://git@github.com/coe-marble/example.git"):
            with self.subTest(url=url):
                self.assertEqual(repository_from_url(url), "coe-marble/example")
        with self.assertRaises(ValueError):
            repository_from_url("https://unrelated.example/owner/repo.git")

    def test_reads_committed_gitlinks_even_when_index_and_gitmodules_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                subprocess.run(["git", "-C", str(root), *args], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            git("init")
            modules_file = root / ".gitmodules"
            modules_file.write_text('[submodule "example"]\n'
                                    '\tpath = src/example\n'
                                    '\turl = git@github.com:coe-marble/example.git\n')
            git("add", ".gitmodules")
            git("update-index", "--add", "--cacheinfo", f"160000,{MODULE.sha},src/example")
            git("-c", "user.name=CI test", "-c", "user.email=ci@example.invalid",
                "commit", "-m", "Pin submodule")
            git("update-index", "--cacheinfo", f"160000,{'b' * 40},src/example")
            modules_file.write_text("# Uncommitted changes must be ignored\n")

            self.assertEqual(pinned_submodules(root), [MODULE])

    def test_latest_failure_overrides_an_older_success(self):
        fetch = Mock(return_value=[run(1), run(2, conclusion="failure")])
        self.assertEqual(inspect_module(MODULE, "ci.yml", fetch).state, "failure")

    def test_api_filters_by_pinned_commit_and_reads_all_pages(self):
        first = [run(number) for number in range(100)]
        payloads = [{"workflow_runs": first, "total_count": 101},
                    {"workflow_runs": [run(100)], "total_count": 101}]
        responses = [io.StringIO(json.dumps(payload)) for payload in payloads]
        with patch("submodule_ci.urlopen", side_effect=responses) as request:
            runs = GitHub("test-token").workflow_runs(MODULE, "ci.yml")

        self.assertEqual(len(runs), 101)
        self.assertEqual(request.call_count, 2)
        for page, entry in enumerate(request.call_args_list, 1):
            self.assertIn(f"head_sha={MODULE.sha}", entry.args[0].full_url)
            self.assertIn(f"page={page}", entry.args[0].full_url)
            self.assertEqual(entry.args[0].get_header("Authorization"), "Bearer test-token")

    def test_rerun_in_progress_is_not_accepted_as_previous_success(self):
        fetch = Mock(return_value=[run(attempt=1), run(status="in_progress", attempt=2)])
        self.assertEqual(inspect_module(MODULE, "ci.yml", fetch).state, "pending")

    def test_only_successful_runs_for_exact_pin_are_accepted(self):
        for conclusion in ("failure", "cancelled", "skipped", "neutral", "timed_out", None):
            with self.subTest(conclusion=conclusion):
                result = inspect_module(MODULE, "ci.yml", lambda *_: [run(conclusion=conclusion)])
                self.assertEqual(result.state, "failure")
        result = inspect_module(MODULE, "ci.yml", lambda *_: [run(sha="b" * 40)])
        self.assertEqual(result.state, "pending")

    def test_pending_ci_is_checked_once_without_retrying(self):
        for runs in ([], [run(status="queued")], [run(status="in_progress")]):
            with self.subTest(runs=runs):
                fetch = Mock(return_value=runs)
                results = collect_results([MODULE], "ci.yml", fetch)
                self.assertEqual(results[0].state, "pending")
                fetch.assert_called_once_with(MODULE, "ci.yml")

    def test_no_ci_results_never_pass(self):
        results = collect_results([MODULE], "ci.yml", lambda *_: [])
        self.assertEqual(results[0].state, "pending")
        self.assertIn("Rerun Submodule CI", summary(results, "ci.yml"))

    def test_failure_and_pending_results_are_reported_in_one_pass(self):
        second = Submodule("src/second", "coe-marble/second", "b" * 40)
        fetch = Mock(side_effect=[[run(conclusion="failure")], []])
        results = collect_results([MODULE, second], "ci.yml", fetch)
        self.assertEqual([result.state for result in results], ["failure", "pending"])
        self.assertEqual(fetch.call_count, 2)

    def test_api_errors_are_reported_without_retrying(self):
        for code, state in ((401, "error"), (403, "error"), (404, "error"),
                            (429, "error"), (503, "error")):
            with self.subTest(code=code):
                fetch = Mock(side_effect=HTTPError("https://api.github.com", code, "", {}, None))
                self.assertEqual(inspect_module(MODULE, "ci.yml", fetch).state, state)
                fetch.assert_called_once()
        fetch = Mock(side_effect=URLError("network unavailable"))
        self.assertEqual(inspect_module(MODULE, "ci.yml", fetch).state, "error")

    def test_exit_status_requires_completed_success_and_does_not_retry(self):
        for runs, expected in (([], 1), ([run(status="queued")], 1), ([run()], 0)):
            with self.subTest(runs=runs), \
                    patch.dict("os.environ", {"GH_TOKEN": "test-token", "GITHUB_STEP_SUMMARY": ""}), \
                    patch("sys.argv", ["submodule_ci.py"]), \
                    patch("submodule_ci.pinned_submodules", return_value=[MODULE]), \
                    patch("submodule_ci.GitHub.workflow_runs", return_value=runs) as fetch, \
                    patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(main(), expected)
                fetch.assert_called_once_with(MODULE, "ci.yml")

    def test_summary_links_to_pin_and_ci_run(self):
        result = Result(MODULE, "success", "success", "https://github.com/runs/1")
        report = summary([result], "ci.yml")
        self.assertIn(f"/commit/{MODULE.sha}", report)
        self.assertIn("[success](https://github.com/runs/1)", report)


if __name__ == "__main__":
    unittest.main()
