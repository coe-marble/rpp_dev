# rpp_dev
Development metapackage for rpp.


# Installation
Run `setup.sh` script from the `rpp_dev` folder

If you plan to use `cpp` components, make sure to build the rpp_cpp using the `colcon build` command

(NOTE): If using with ROS2, make sure you have sourced the environment in the terminal that runs GUI. In addition,
configure the rpp to use ros2 compilation by running `rpp registry config USE_ROS2_COMPILATION=True`. This setting is global.

# Getting started

Usefull commands:

`rpp pm` starts a Plugin Manager GUI

`rpp ws` starts a Workspace GUI


# Packages

- [rpp_cli](https://github.com/coe-marble/rpp_cli.git) - Command line interface for rpp
- [rpp_common](https://github.com/coe-marble/rpp_common.git) - Common utilities, plugin type definitions, and plugin description definitions for rpp
- [rpp_orchestrator](https://github.com/coe-marble/rpp_orchestrator.git) - Orchestrator for managing rpp components and workflows
- [rpp_plugin_registrator](https://github.com/coe-marble/rpp_plugin_registrator.git) - Plugin and plugin type management system for rpp
- [rpp_testing](https://github.com/coe-marble/rpp_testing.git) - Testing utilities for rpp

## Language Support
- [rpp_cpp](https://github.com/coe-marble/rpp_cpp.git) - C++ support for rpp
- [rpp_py](https://github.com/coe-marble/rpp_py.git) - Python support for rpp


