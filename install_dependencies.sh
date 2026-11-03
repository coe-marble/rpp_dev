#!/usr/bin/env bash
set -euo pipefail

venv_python=$(command -v python3)

if [ ! -x "$venv_python" ]; then
    echo "Virtual environment Python not found in PATH." >&2
    exit 1
fi

if ! "$venv_python" -c 'import sys; raise SystemExit(sys.prefix == sys.base_prefix)'; then
    echo "Active Python is not a virtual environment." >&2
    exit 1
fi

repository_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

for project_dir in "${repository_dir}"/src/*; do
    [ -f "${project_dir}/pyproject.toml" ] || continue
    # The RPP packages are installed as editable packages by setup.sh with
    # --no-deps. Reinstalling them as editable packages here lets pip resolve
    # their declared dependencies without requiring a version-specific pip
    # option such as --only-deps.
    "$venv_python" -m pip install --no-cache-dir -e "$project_dir"
done
