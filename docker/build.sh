#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
image_tag="${IMAGE_TAG:-ghcr.io/coe-marble/rpp-dev:lyrical}"

DOCKER_BUILDKIT=1 docker build \
    --ssh default \
    --tag "${image_tag}" \
    --file "${script_dir}/Dockerfile" \
    "$@" \
    "${script_dir}"
