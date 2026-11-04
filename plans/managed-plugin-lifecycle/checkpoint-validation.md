# Native lifecycle foundation checkpoint

Date: 2026-11-04.

This checkpoint provides lifecycle callbacks/results, native typed handover,
schema bindings and generation, context-tree traversal, and construction-owned
Python transports. Managers, application call gates, remote lifecycle control,
reload, ROS bridges, and spawners remain separate work.

## Coordinated revisions

| Repository | Commit | PR base |
| --- | --- | --- |
| `rpp_common` | `08d66bf` | `main` |
| `rpp_cpp` | `ddd1c35` | `lyrical` |
| `rpp_py` | `99aa9dc` | `main` |
| `rpp_plugin_registrator` | `93c983e` | `main` |
| `rpp_testing` | `bd9025d` | `main` |

The `rpp_dev` gitlinks pin the complete commits. The C++ base preserves the
existing Lyrical integration without adding its earlier commits to this review.
Regenerate interfaces and rebuild C++ artifacts together; the old initializer
API is removed and binary compatibility is not provided.

## Validation

The combined source revisions were tested in an isolated ROS Lyrical workspace
with Cap'n Proto 1.1.0. Source files tested before committing are identical to
the component commits above.

- Python runtime and registrator suites: **218 passed**, including all nine
  native/adapted runtime integration cases and the real generated C++ adapter
  compilation/link/execution checks.
- C++ build and behavioral suites: **38 passed**, across five GTest targets.
- Formatting, CMake lint, and XML lint passed. All nine CTest targets completed
  successfully. The result summary reports 43 skips: these are cppcheck checks
  skipped by the installed cppcheck 2.19.0 integration for its performance issue;
  no C++ behavioral tests were skipped.

Commands, from the integration workspace with ROS and its install sourced and
`RPP_CPP_CORE_PATH` pointing to `build/rpp_cpp`:

```bash
python3 -m pytest -q rpp_dev/src/rpp_py/tests rpp_dev/src/rpp_plugin_registrator/tests
ctest --test-dir build/rpp_cpp --output-on-failure
colcon test-result --test-result-base build/rpp_cpp/test_results --verbose
```

The C++ targets were built with `BUILD_TESTING=ON` and the existing two-pass
generated-source build used in component CI. The runtime/fixture packages must
be installed or available on `PYTHONPATH` as in CI.

## PR and CI coordination

The generator, Python runtime, C++ runtime, and shared fixtures are a coordinated
API migration. Their PRs must not be evaluated against an arbitrary mixture of
old and new dependencies.

Use the existing `workflow_dispatch` entry point of each component's `ci.yml`
on `feature/managed-lifecycles`. Integration workflows then check out that same
branch of `rpp_dev`, which pins these revisions. No extra build job is added to
the metarepository. Its aggregate CI reads results for the pinned SHAs.

Automatic component PR workflows currently select the integration base branch;
those runs can use older dependencies before these linked changes are merged.
Record coordinated manual CI results on each PR and verify the final pins after
merge. The `more_simulation` migration is excluded from this checkpoint.
