# Developing with the Docker image

The image contains a fully configured and installed RPP workspace. To make its
sources editable, copy the complete workspace from a stopped container and
bind-mount it back at exactly the same path. This preserves the generated
`build/` and `install/` directories and keeps the RPP library registrations
valid.

Container filesystem changes are lost when a container is removed, so temporary development containers should not be the only copy of your work. To make the workspace persistent, export its configured files to the host once. Bind-mount that host copy back at the same path whenever you start a development container.

## 1. Obtain the image

The published image is `ghcr.io/coe-marble/rpp-dev:lyrical`:

```bash
docker pull ghcr.io/coe-marble/rpp-dev:lyrical
```

Alternatively, build a local image:

```bash
./build.sh
```

The build script defaults to `ghcr.io/coe-marble/rpp-dev:lyrical`. Set
`IMAGE_TAG` before running the script to use a different tag.

## 2. Export the configured workspace

Run these commands from an empty development directory on the host:

```bash
docker create --name rpp-dev-export ghcr.io/coe-marble/rpp-dev:lyrical
docker cp rpp-dev-export:/workspaces/rpp/ros2_ws ./ros2_ws
docker rm rpp-dev-export
```

`docker create` makes a stopped container only; it does not start the image.
The copy includes the source repositories and the workspace's `build/`,
`install/`, and `log/` directories.

## 3. Develop using the exported workspace

```bash
docker run --rm -it \
    --mount type=bind,src="$(pwd)/ros2_ws",dst=/workspaces/rpp/ros2_ws \
    --workdir /workspaces/rpp/ros2_ws \
    ghcr.io/coe-marble/rpp-dev:lyrical
```

The bind mount replaces the image's workspace with the host copy at the same
absolute path. RPP's existing editable installs and library registrations
therefore remain valid, while source changes are made directly on the host.

After changing C++ sources, rebuild from inside the container and re-source
the workspace:

```bash
colcon build --symlink-install --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
```
