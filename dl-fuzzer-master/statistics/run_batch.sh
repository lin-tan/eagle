#!/bin/bash
#### usage
# $ bash run_batch.sh /absolute path/to/constraints/constraints_1/changed [expect_ok|expect_exception] [prev_ok|permute] [tensorflow|pytorch|mxnet]

# change $home
#baseline: bash run_batch.sh .../changed expect_ok prev_ok tensorflow no_constr no_adapt
#adt_nc (baseline+adpt):  bash run_batch.sh .../changed expect_ok prev_ok tensorflow no_constr adapt
#eo_nat: bash run_batch.sh .../changed expect_ok prev_ok tensorflow constr no_adapt


home='/home' # '/Users/danning/Desktop/deepflaw/exp2' "/home"
expect_ok="expect_ok"
expect_excpt="expect_exception"
# prev_ok="prev_ok"
# permute="permute"
repo_name="dl-fuzzer"   #"DocTer-Ext" "dl-fuzzer"


constraints_folder=$1
obey=$2
# adapt=$3
package=$3
constr=$4
# adaptive_gen=$6
if [ $# -ne 4 ]
  then
    echo "Need 4 arguments: 1) path to constraints folder, 2) obey option [expect_ok|expect_exception], 3) python package [tensorflow|pytorch|mxnet], 4) following constraints [ constr | no_constr]." 
    exit 0
fi
if [[ "$package" != "tensorflow" && "$package" != "pytorch" && "$package" != "mxnet" && "$package" != "sklearn" ]];then
  echo "Error: unsupported package choice: $package"
  exit 1
fi
if [ "$obey" == "$expect_ok" ]; then
    subdir=$expect_ok"_"$constr
    # subdir=$expect_ok"_"$constr"_"$adaptive_gen
else
    subdir=$expect_excpt"_"$constr
    # subdir=$expect_excpt"_"$constr"_"$adaptive_gen
fi
WORKDIR="$home"/workdir/"$subdir"
workorder_record="$WORKDIR"/"record_work"
division_id=$( basename "$constraints_folder" )
division_record="$WORKDIR"/"${division_id}_record"
if [ -f "$workorder_record" ]; then
  echo "... record_work exists ..."
else
  mkdir -p "$WORKDIR"
  touch "$workorder_record"
  touch "$division_record"
fi

FUZZERGIT="$home"/code/"$repo_name"

for c in "$constraints_folder"/*; do
  name=$( basename "$c" )
  if grep -qw "$name" "$workorder_record"; then
    echo "Skipping $name"
    continue
  else
    echo "$name" >> $workorder_record
    echo "$name" >> "$division_record"
  fi

  workdir="$WORKDIR/${name}_workdir"
  mkdir -p "$workdir"
  echo "$workdir"
  dump_folder="$workdir"/".dump"
  mkdir -p "$dump_folder"
  args=(
    "$c"
    "${FUZZERGIT}/${package}/${package}_dtypes.yml"
    "--workdir=$workdir"
    # "--cluster"
    # "--dist_threshold=0.5"
    # "--dist_metric=jaccard"
    # "--adapt_to=$adapt"
    # "--fuzz_optional"
    "--fuzz_optional_p=0.6"
    # "--special_value" # drop nan and inf
    "--gen_script"
    "--timeout=10"
    "--model_test"
    "--check_nan"
    # "--save"
  )
  if [ "$constr" == "no_constr" ]; then # baseline
    args+=("--ignore")
    args+=("--mutate_p=0")    # force disabling mutation (baseline)
    args+=("--guided_mutate")
    args+=("--max_iter=2000")

  else 
    args+=("--mutate_p=0.2")   
    # args+=("--mutate_p=0")
    args+=("--guided_mutate")
    
    if [ "$obey" == "$expect_ok" ]; then
      args+=("--max_iter=1200")
    else
      args+=("--max_iter=800")
    fi
  fi

  if [ "$obey" == "$expect_ok" ]; then
    args+=("--obey")
  fi

  if [ "$package" == "pytorch" ];then
    args+=("--data_construct=tensor")
  elif [ "$package" == "mxnet" ];then
    args+=("--data_construct=nd.array")
  fi

  
  # if [ "$adaptive_gen" == "adapt" ];then
  #   args+=("--consec_fail=10")
  # else
  #   args+=("--consec_fail=2000")
  # fi
  pushd "$dump_folder" > /dev/null
  echo "running in"
  pwd
  # echo "python ${FUZZERGIT}/fuzzer/fuzzer-driver.py "
  # echo "${args[@]}"
  # echo "python ${FUZZERGIT}/fuzzer/fuzzer-driver.py "${args[@]}" &> $workdir/out"
  python ${FUZZERGIT}/fuzzer/fuzzer-driver.py "${args[@]}" &> $workdir/out
  popd > /dev/null
  rm -r "$dump_folder"
  status=$?
  if [ $status -eq 0 ];then
    status_msg="ok"
  else
    status_msg="fail"
  fi
  echo "===  $( basename "$c" ) ===    $status_msg"
<<'user_input'
  echo "continue? [y/n]"
  read -r go_on
  if [ "$go_on" == "y" ]; then
    continue
  else  # anything other than 'y' will break
    break
  fi
user_input
done

echo "finished"
