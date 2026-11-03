# RPP test container

This image supplies the stable, expensive test prerequisites shared by the
RPP C++, Python runtime, and registrator workflows:

- Ubuntu 26.04 through the ROS 2 Lyrical base image;
- ROS 2 Lyrical, CMake, Ninja, colcon, pybind11, spdlog, and nlohmann-json;
- Cap'n Proto 1.1.0, verified during the image build; and
- the declared third-party Python test dependencies in `/opt/rpp-test-venv`.

It deliberately does not contain RPP source packages. CI checks out the
revision under test and installs those packages editable, keeping source
changes independent from the image cache.

## Build locally

```bash
./build.sh
```

The default tag is
`ghcr.io/coe-marble/rpp-test-container:lyrical-ubuntu26.04-capnp1.1.0-v1`.
Set `IMAGE_TAG` to use another tag.

## Publishing and access

`.github/workflows/test-container.yml` builds the image when this directory
changes and publishes it to GitHub Container Registry on pushes to `main` or
`develop`. Before private repositories consume the image, grant their
GitHub Actions access to the `rpp-test-container` package and give the
existing `RPP_CI_TOKEN` secret the `read:packages` scope.
