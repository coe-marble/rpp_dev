install_only=false

case "$#:$1" in
    0:)
        ;;
    1:--install|1:--instal)
        install_only=true
        ;;
    *)
        echo "Usage: $0 [--install]" >&2
        exit 1
        ;;
esac

venv_python=$(command -v python3)

if [ ! -x "$venv_python" ]; then
    echo "Virtual environment Python not found in PATH..." >&2
    exit 1
fi

if ! "$venv_python" -c 'import sys; raise SystemExit(sys.prefix == sys.base_prefix)'; then
    echo "Active Python is not a virtual environment..." >&2
    exit 1
fi

venv_pip() {
    "$venv_python" -m pip "$@"
}

if [ "$install_only" = false ]; then
    sudo apt-get install -y \
        capnproto=1.1.0-2.1 \
        libcapnp-dev=1.1.0-2.1 \
        python3-pyqt6 \
        pybind11-dev \
        nlohmann-json3-dev \
        gdb

    git submodule update --init --recursive --remote
fi

checkout_develop() {
    if [ "$install_only" = false ]; then
        git checkout develop
    fi
}

if ! bash "$(dirname "${BASH_SOURCE[0]}")/install_dependencies.sh"; then
    echo "RPP dependency installation failed." >&2
    exit 1
fi

cd src

cd rpp_cli
checkout_develop
venv_pip install --no-deps -e .
cd ..

cd rpp_common
checkout_develop
venv_pip install --no-deps -e .
cd ..

cd rpp_orchestrator
checkout_develop
venv_pip install --no-deps -e .
cd ..

cd rpp_plugin_registrator
checkout_develop
venv_pip install --no-deps -e .
cd ..

cd rpp_py
checkout_develop
venv_pip install --no-deps -e .
cd ..

cd rpp_testing
checkout_develop
venv_pip install --no-deps -e .
cd ..
