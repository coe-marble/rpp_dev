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

Each RPP repository runs its workflow on pushes to `develop` and on pull
requests targeting `develop`. Component workflows assemble the full RPP
integration checkout so they can test cross-package behavior. If the
repositories are private, configure an `RPP_CI_TOKEN` repository secret with
read access to all `coe-marble` RPP repositories.


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


