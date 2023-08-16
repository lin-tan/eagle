#!/bin/bash
# this script should be run within the docker container for getting coverage

package=$1
if [ -z "$package" ]; then
  echo "Error: need to specify a package [tensorflow | torch | mxnet]"
  exit 1
elif [[ "$package" != "tensorflow" && "$package" != "torch" && "$package" != "mxnet" ]];then
  echo "Error: unsupported package choice: $package"
  exit 1
fi

# install coverage related packages
bash install_cov.sh

divs_folder="$2"
cd "$divs_folder" || { echo "Failed to change directory"; exit 1; }

# NOTE: it seems pytest needs to be invoked from a certain input_dir to make the coverage work
# simply passing a path to it doesn't always work
pytest --cov="$package" --boxed --cov-report=html --cov-branch .
