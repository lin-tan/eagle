#!/bin/bash

package=$1
division_count=$2
docker_home=$3 #"/local1/m346kim/dl-fuzzing/expr/pytorch/docker_1_935c4f"
docker_surfix=$4
division_root=$5
choice=$6

division_root=$( realpath "$division_root" )
if [ $# -ne 6 ]
  then
    echo "Need 6 arguments:
         1) python package (tensorflow|torch|mxnet),
         2) division count for constraints. e.g., 10,
         3) docker home to be mounted,
         4) docker surfix (e.g., nc_mx), and
         5) path to the divided folders
         6) processing choice (cov|res)"
    exit 1
fi

if [ -z "$package" ]; then
  echo "Error: need to specify a package [tensorflow | torch | mxnet]"
  exit 1
elif [[ "$package" != "tensorflow" && "$package" != "torch" && "$package" != "mxnet" ]];then
  echo "Error: unsupported package choice: $package"
  exit 1
fi

if [ "$choice" == "cov" ];then
  cmd="get_coverage.sh"
elif [ "$choice" == "res" ];then
  cmd="get_output.sh"
else
  echo "Error: unknown choice: $choice"
fi

for (( i=1;i<=division_count;i++ ))
do
  # creating tmux sessions
  container_name="${package}_${i}_${docker_surfix}"
  division_folder="$division_root/division_$i"
  tmux new -d -s "$container_name"
  tmux send-keys -t "$container_name" \
  "bash create_container_run.sh ${package} ${container_name} ${docker_home} ${division_folder} ${choice}" C-m
done
