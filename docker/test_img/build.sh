#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
image_tag="${IMAGE_TAG:-ghcr.io/coe-marble/rpp-test-container:lyrical-ubuntu26.04-capnp1.1.0-v1}"

DOCKER_BUILDKIT=1 docker build \
    --tag "${image_tag}" \
    --file "${script_dir}/Dockerfile" \
    "${script_dir}"
