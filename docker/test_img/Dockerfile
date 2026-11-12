# syntax=docker/dockerfile:1.7
FROM ros:lyrical-ros-base

ARG CAPNP_PACKAGE_VERSION=1.1.0-2.1

LABEL org.opencontainers.image.source="https://github.com/coe-marble/rpp_dev"
LABEL org.opencontainers.image.description="RPP continuous-integration prerequisites"

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=lyrical
ENV RPP_USE_ROS2_COMPILATION=true

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        ca-certificates \
        capnproto=${CAPNP_PACKAGE_VERSION} \
        cmake \
        gdb \
        git \
        libcapnp-dev=${CAPNP_PACKAGE_VERSION} \
        libeigen3-dev \
        libspdlog-dev \
        ninja-build \
        nlohmann-json3-dev \
        pkg-config \
        pybind11-dev \
        python3-colcon-common-extensions \
        python3-dev \
        python3-pip \
        python3-venv \
        ros-lyrical-ament-index-python \
        ros-lyrical-ament-cmake-gtest \
        ros-lyrical-angles \
        ros-lyrical-diagnostic-msgs \
        ros-lyrical-diagnostic-updater \
        ros-lyrical-geometry-msgs \
        ros-lyrical-launch-testing \
        ros-lyrical-launch-testing-ament-cmake \
        ros-lyrical-nav-msgs \
        ros-lyrical-rclcpp \
        ros-lyrical-rclpy \
        ros-lyrical-rosbag2-storage-mcap \
        ros-lyrical-rosbag2-transport \
        ros-lyrical-rosidl-default-generators \
        ros-lyrical-sensor-msgs \
        ros-lyrical-std-msgs \
        ros-lyrical-std-srvs \
        ros-lyrical-tf2 \
        ros-lyrical-tf2-geometry-msgs \
        ros-lyrical-tf2-ros \
        rsync \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv --system-site-packages /opt/rpp-test-venv \
    && /opt/rpp-test-venv/bin/python -m pip install --no-cache-dir --upgrade pip \
    && /opt/rpp-test-venv/bin/python -m pip install --no-cache-dir \
        "pydantic>=2,<3" \
        "json5>=0.9,<1" \
        "pycapnp>=1.3,<3" \
        "pytest>=8,<9" \
        "tree-sitter>=0.21,<0.27" \
        "tree-sitter-cpp>=0.21,<0.24" \
        "xmltodict>=0.12,<1"

ENV PATH="/opt/rpp-test-venv/bin:${PATH}"

WORKDIR /workspace
