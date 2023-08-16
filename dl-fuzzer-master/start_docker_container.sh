#!/bin/bash

name="$1"
image="$2"
mem_limit="4g"

if [[ -z "$name" ]];then
  echo "Error: need a name to tag the container"
  exit 1
fi

if [[ -z "$image" ]];then
  echo "Error: need an image name to start the container"
  exit 1
fi

cmd="docker run -it --rm --memory=$mem_limit --memory-swap=$mem_limit --name $name $image"
echo "Will run command:"
echo "    $cmd"

eval "$cmd"
