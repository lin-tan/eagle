#!/bin/bash


package=$1
# docker_home=$3 #"/local1/m346kim/dl-fuzzing/expr/pytorch/docker_1_935c4f"
exp_id=$2
expr_dir="/local1/xdanning/docter/expr"
source_path="/local1/xdanning/docter/code/dl-fuzzer"  # need to update if dir changed
modes=("eo" "ee") # ("baseline" "eo" "ee")
if [ $# -lt 2 -o  $# -gt 3 ]
  then
    echo "Need 2 or 3 arguments: 
        1) python package (tensorflow|pytorch|mxnet), 
        2) exp_id
        3) Optional: division count for constraints. Default: 1."
    exit 0
fi

# set division count
if [ -z $3 ];then
    echo "Set division count as 1 by default."
    division_count=1
else
    division_count=$3
fi

# set workdir path
if [ "$package" == "tensorflow" ]; then
    workdir_name="TF"$exp_id
    workdir_path=$expr_dir"/tensorflow"
elif [ "$package" == "pytorch" ]; then
    workdir_name="PT"$exp_id
    workdir_path=$expr_dir"/pytorch"
elif [ "$package" == "mxnet" ]; then
    workdir_name="MX"$exp_id
    workdir_path=$expr_dir"/mxnet"
elif [ "$package" == "sklearn" ]; then
    workdir_name="SK"$exp_id
    workdir_path=$expr_dir"/sklearn"
else
  echo "Error: unsupported package choice: $package"
  exit 1
fi

# get commit ID as folder suffix
commitID=$(git rev-parse HEAD| cut -c1-7)

# setup workdir
for mode in ${modes[@]}; do
    new_dir_name=$workdir_name"_"$commitID"_"$mode
    new_dir_path=$workdir_path"/"$new_dir_name      # also docker home
    mkdir -p -v $new_dir_path
    mkdir -v $new_dir_path"/code"
    mkdir -v $new_dir_path"/workdir"

    pushd $new_dir_path"/code" > /dev/null
    # set up code folder
    cp -r $source_path .
    # mv DocTer-Ext dl-fuzzer
    # echo "$new_dir_path created!"

    # start experiment
    code_dir=$new_dir_path"/code/dl-fuzzer"
    echo "bash $code_dir/statistics/run_docker_setup.sh $package $division_count $new_dir_path $new_dir_name $mode"
    bash $code_dir/statistics/run_docker_setup.sh $package $division_count $new_dir_path $new_dir_name $mode
    
    #rm -r ./dl-fuzzer # (to save space) delete the code automatically after the experiment
    popd > /dev/null

done
