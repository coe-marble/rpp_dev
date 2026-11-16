#!/bin/bash

cd src

cd rpp_cli
echo "Pushing rpp_cli"
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_common
echo "Pushing rpp_common"
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_cpp
echo "Pushing rpp_cpp"
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_orchestrator
echo "Pushing rpp_orchestrator"
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_plugin_registrator
echo "Pushing rpp_plugin_registrator"
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_py
echo "Pushing rpp_py"
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_testing
echo "Pushing rpp_testing"
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_ros2
echo "Pushing rpp_ros2"
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd rpp_demos
echo "Pushing rpp_demos"
git add .
git commit -m "${1:-"Update"}"
git push
cd ..

cd ../rpp_docs
git add .
echo "Pushing rpp_docs"
git commit -m "${1:-"Update"}"
git push
cd ..


git add .
echo "Pushing rpp_dev"
git commit -m "${1:-"Update"}"
git push

