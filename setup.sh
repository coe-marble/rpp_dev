git submodule update --init --recursive
cd src

cd rpp_cli
git checkout main
pip3 install -e .
cd ..

cd rpp_common
git checkout main
pip3 install -e .
cd ..

cd rpp_orchestrator
git checkout main
pip3 install -e .
cd ..

cd rpp_plugin_registrator
git checkout main
pip3 install -e .
cd ..

cd rpp_py
git checkout main
pip3 install -e .
cd ..

cd rpp_testing
git checkout main
pip3 install -e .
cd ..

