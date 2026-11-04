# rpp_dev
Development metapackage for rpp.


# Installation
Run `setup.sh` script from the `rpp_dev` folder

The setup requires the explicitly pinned system packages `capnproto=1.1.0-2.1`
and `libcapnp-dev=1.1.0-2.1`. Python runtime dependencies are declared in each
package's `pyproject.toml`; test-only dependencies are exposed through its
`[test]` extra and are installed by CI from that metadata.

If you plan to use C++ components, build `rpp_cpp` with CMake. `colcon build`
remains supported when using a ROS 2 workspace.

```bash
cmake -S src/rpp_cpp -B build/rpp_cpp
cmake --build build/rpp_cpp
```

(NOTE): If using with ROS2, make sure you have sourced the environment in the terminal that runs GUI. In addition,
configure RPP to use ROS 2 compilation by running
`rpp registry config set USE_ROS2_COMPILATION true`. This setting is global.

# Getting started

Usefull commands:

`rpp pm` starts a Plugin Manager GUI

`rpp ws` starts a Workspace GUI

Further information on the rpp workflows can be found in the [documentation](rpp_docs/docs/workflows.md)

## Continuous integration

`rpp_dev` aggregates the existing CI results of its pinned submodule commits.
Its **Submodule CI** workflow runs on pushes and pull requests to `main` and
`develop`, and can also be started manually. It does not build packages or
rerun their tests.

The job uses the `delayed-ci` environment. In **Settings → Environments →
delayed-ci**, enable a **10-minute wait timer**. GitHub holds the job before
allocating a runner, so this delay does not consume runner minutes. The timer
is configured in repository settings, not in the workflow YAML.

For every submodule in the committed `.gitmodules`, including documentation,
the workflow checks the latest `ci.yml` run for the exact recorded commit.
All must already have finished with `success`. Each submodule is checked once;
the job exits immediately after collecting the results, without sleeping or
polling. Missing or unfinished runs are reported as pending and cause a
nonzero exit code. Failed, cancelled, skipped, or inaccessible runs also do
not pass. The job summary links each pinned commit and its CI result. After
the submodule workflows finish, rerun **Submodule CI** to refresh the result.

For private repositories, configure an `RPP_CI_TOKEN` repository secret with
**Actions: read** access to every submodule repository. A fine-grained personal
access token or GitHub App token can provide this permission. The default
`GITHUB_TOKEN` only has access to `rpp_dev`; it cannot read private submodules.
Component workflows may also require **Contents: read** for their existing
cross-repository checkouts. Branch protection should require the **Submodule
CI** job instead of the former integration-test job.

To run the same check locally with a suitable token in `GH_TOKEN`:

```bash
python3 .github/scripts/submodule_ci.py
```

The checker uses only Python's standard library. Its own regression tests run
without GitHub access:

```bash
python3 -m unittest discover -s .github/scripts -p 'test_*.py'
```


## Using ROS2 with RPP

If you plan to use ROS2 with RPP, after building, source
the workspace before launching RPP:

```bash
cd ros_ws
colcon build --symlink-install
source install/setup.bash
```

For ROS 2 compilation, also enable the global RPP setting:

```bash
rpp registry config set USE_ROS2_COMPILATION true
```

# Packages

- [rpp_cli](https://github.com/coe-marble/rpp_cli.git) - Command line interface for rpp
- [rpp_common](https://github.com/coe-marble/rpp_common.git) - Common utilities, plugin type definitions, and plugin description definitions for rpp
- [rpp_orchestrator](https://github.com/coe-marble/rpp_orchestrator.git) - Orchestrator for managing rpp components and workflows
- [rpp_plugin_registrator](https://github.com/coe-marble/rpp_plugin_registrator.git) - Plugin and plugin type management system for rpp
- [rpp_testing](https://github.com/coe-marble/rpp_testing.git) - Testing utilities for rpp

## Language Support
- [rpp_cpp](https://github.com/coe-marble/rpp_cpp.git) - C++ support for rpp
- [rpp_py](https://github.com/coe-marble/rpp_py.git) - Python support for rpp


