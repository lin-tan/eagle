#!/bin/bash
package=$1
container_name=$2
docker_home=$3
division_folder=$4
choice=$5

if [ "$package" == "tensorflow" ];then
  docker_image="dlfuzzer-tf-2.1.0:latest"
elif [ "$package" == "torch" ];then
  docker_image="dlfuzzer-pytorch-1.5.0:latest"
elif [ "$package" == "mxnet" ];then
  docker_image="dlfuzzer-mxnet-1.6.0:latest"
else
  echo "Error: unsupported package choice: $package"
  exit 1
fi

mem_limit="4g"

run_options=(
  -v "$docker_home:/home:ro"
  -v "/local1/y2647li/dl-fuzzer:/code:ro"
  -v "$division_folder:/div"
  --memory="$mem_limit"
  --memory-swap="$mem_limit"
  --name "$container_name"
  -it
  --rm
  #-d
  -w "/code/tool/set_docker_run/"
)

if [ "$choice" == "cov" ];then
  cmd="get_coverage.sh"
elif [ "$choice" == "res" ];then
  cmd="get_output.sh"
else
  echo "Error: unknown choice: $choice"
fi

echo "Creating a docker container for $container_name..."
docker run "${run_options[@]}" "$docker_image" "/bin/bash" "$cmd" "$package" "/div"
