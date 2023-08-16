#!/bin/bash

package=$1
division_count=$2 
docker_home=$3 #"/local1/m346kim/dl-fuzzing/expr/pytorch/docker_1_935c4f"
docker_surfix=$4
mode=$5   # eo/ee/baseline
if [ $# -ne 5 ]
  then
    echo "Need 5 arguments: 1) python package (tensorflow|pytorch|mxnet), 2) division count for constraints. e.g., 10, 3) docker home to be mounted, 4) docker surfix (e.g., nc_mx), and 5) mode (ee/eo/baseline)."
    exit 0
fi

if [ "$mode" == "baseline" ]; then
  expects=("expect_ok")
  constr="no_constr" 
elif [ "$mode" == "eo" ]; then
  expects=("expect_ok")
  constr="constr" 
elif [ "$mode" == "ee" ]; then
  expects=("expect_exception")
  constr="constr" 
else
  echo "Error: unsupported mode choice: $mode"
  exit 1
fi

############## Variables To Set  #############
mem_limit="4g"
# expects=("expect_ok")  # "expect_exception")
# expects=("expect_exception")
# modes=("prev_ok")
# constr="no_constr"  #[constr | no_constr]
# adaptive_gen="no_adapt" #[adapt | no_adapt]
##############################################

fuzzer_repo="/home/code/dl-fuzzer" # In docker 
if [ "$package" == "tensorflow" ];then
  docker_image="dlfuzzer-tf-2.1.0:latest"
  # rel_dir="doc_analysis/subtree_mine/constr/tf/success"
  rel_dir="doc_analysis/subtree_mine/constr/tf/fixformat"
elif [ "$package" == "pytorch" ];then
  docker_image="dlfuzzer-pytorch-1.5.0:latest"
  rel_dir="doc_analysis/subtree_mine/constr/pt/bl"
elif [ "$package" == "mxnet" ];then
  docker_image="dlfuzzer-mxnet-mkl-1.6.0:latest"
  # rel_dir="doc_analysis/subtree_mine/constr/mx/success"
  rel_dir="doc_analysis/subtree_mine/constr/mx/mx7-3eo"
elif [ "$package" == "sklearn" ];then
  docker_image="dlfuzzer-sklearn-0.24.2:latest"
  # rel_dir="doc_analysis/extract_constraint/tmp_data/sk1_data"
  rel_dir="doc_analysis/extract_constraint/sklearn/constr_all/changed"
else
  echo "Error: unsupported package choice: $package"
  exit 1
fi


constraints_dir=$fuzzer_repo"/"$rel_dir
real_constraints_dir=$docker_home"/code/dl-fuzzer/"$rel_dir

echo "Reading yaml files from $real_constraints_dir"

# divide yaml files into $division_count groups to support parallel runnings 
pushd $real_constraints_dir > /dev/null
numfiles=(*.yaml)
numfiles=${#numfiles[@]}
group_size=$(echo $((numfiles / division_count + 1)))
echo "Total $numfiles yaml files to be divided into $division_count groups. $group_size yaml files in each division"

group_counter=$division_count
new_dir_name=$real_constraints_dir"/division_"${group_counter}
mkdir -p "$new_dir_name"
echo "New division created $new_dir_name"
yaml_counter=0
for c in $( find . -maxdepth 1 -name '*.yaml' -type f | shuf ); do
  yaml_counter=$(( $yaml_counter + 1 ))
  name=$( basename "$c" )
  cp $name $new_dir_name
  if [ $yaml_counter -ge $group_size ]; then
    yaml_counter=0
    group_counter=$(( $group_counter + 1 ))
    new_dir_name=division_"${group_counter}"
    mkdir -p $new_dir_name
    echo "New division created $new_dir_name"
  fi
done
echo "Total $group_counter divisions created"
popd > /dev/null

# done dividsion


for exp in "${expects[@]}"
do
  # for mode in "${modes[@]}"
  # do
  echo "===== Processing ${package}_${exp}_${constr} =====" 
#<<start_screen
  for ((i=1;i<=$division_count;i++))
  do
    mode_id=${package}"_"${exp}"_"${i}"_"${docker_surfix}
    echo "Creating a docker container for $mode_id..."
    docker run -v $docker_home:/home --memory=$mem_limit --memory-swap=$mem_limit --name $mode_id -it -d $docker_image
    sleep 1
  done

  for ((i=1;i<=$division_count;i++))
  do
    mode_id=${package}"_"${exp}"_"${i}"_"${docker_surfix}
    docker exec $mode_id bash -c "mkdir -p /home/workdir"
    echo "Creating a screen in container $mode_id... DETACH MANUALLY!!"
    sleep 1
    docker exec -it $mode_id screen -S $mode_id -m bash -c "bash"
    sleep 1
  done

  for ((i=1;i<=$division_count;i++))
  do
    mode_id=${package}"_"${exp}"_"${i}"_"${docker_surfix}
#     echo "Activating conda env in container $mode_id..."
#     docker exec -it $mode_id screen -S $mode_id -X stuff "conda activate fuzzer-test^M" 
#     sleep 1
    echo "Executing run_batch.sh in screen at container $mode_id..."
    docker exec -it $mode_id screen -S $mode_id -X stuff "bash ${fuzzer_repo}/statistics/run_batch.sh ${constraints_dir}/division_${i} $exp $package $constr | tee /home/workdir/${mode_id}.out^M"
    sleep 1
#start_screen

<<quit_screen
    for ((i=1;i<=$division_count;i++))
    do
      mode_id=${exp}"_"${i}"_"${docker_surfix}
      echo "Quitting screen in container $mode_id."
      docker exec -it $mode_id screen -S $mode_id -X quit
      sleep 1
    done
quit_screen
  done #mode
done #exp

