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
        git \
        libcapnp-dev=${CAPNP_PACKAGE_VERSION} \
        libspdlog-dev \
        libxkbcommon0 \
        ninja-build \
        nlohmann-json3-dev \
        pybind11-dev \
        python3-colcon-common-extensions \
        python3-dev \
        python3-pip \
        python3-venv \
        ros-lyrical-rclcpp \
        rsync \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/rpp-test-venv \
    && /opt/rpp-test-venv/bin/python -m pip install --no-cache-dir --upgrade pip \
    && /opt/rpp-test-venv/bin/python -m pip install --no-cache-dir \
        "PyQt6>=6.4,<7" \
        "pydantic>=2,<3" \
        "json5>=0.9,<1" \
        "pycapnp>=1.3,<3" \
        "pytest>=8,<9" \
        "tree-sitter>=0.21,<0.27" \
        "tree-sitter-cpp>=0.21,<0.24" \
        "xmltodict>=0.12,<1"

ENV PATH="/opt/rpp-test-venv/bin:${PATH}"

WORKDIR /workspace
