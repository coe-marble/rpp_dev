#!/bin/bash

cd src

cd rpp_cli
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_common
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_cpp
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_orchestrator
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_plugin_registrator
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_py
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_testing
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

