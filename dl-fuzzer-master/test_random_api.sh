#!/bin/bash
#### usage
# $ bash test_obey.sh package_name path_to_constraints permute|prev_ok [target_list_file]
# Note: if no target_list_file is provided, then the script will
# try to run every file under path_to_constraints
# everything will be stored in WORKDIR
package=$1
if [ -z "$package" ]; then
  echo "Error: need to specify a package [tensorflow | pytorch | mxnet]"
  exit 1
elif [[ "$package" != "tensorflow" && "$package" != "pytorch" && "$package" != "mxnet" ]];then
  echo "Error: unsupported package choice: $package"
  exit 1
fi

WORKDIR=".workdir_$package"
mkdir -p "$WORKDIR"
workorder_record="$WORKDIR"/"record_work"

if [[ -f "$workorder_record" ]]; then
  echo "... record_work exists ..."
else
  touch "$workorder_record"
fi

if_follow_constraints=$2
if [[ -z "$if_follow_constraints" ]];then
  echo "Error: must specify whether to follow or violate the constraints, options: [follow | violate]"
  exit 1
elif [[ "$if_follow_constraints" != "follow" && "$if_follow_constraints" != "violate" ]]; then
  echo "Error: only 'follow' or 'violate' are allowed for this argument"
  exit 1
fi

constraints_folder=$3
if [[ -z "$constraints_folder" ]];then
  echo "Error: constraints folder is not given"
  exit 1
fi

adapt_to_opt=$4
if [[ -z "$adapt_to_opt" ]];then
  echo "Error: fuzzer option '--adapt_to' is not given"
  exit 1
fi

if [[ "$adapt_to_opt" != "prev_ok" && "$adapt_to_opt" != "permute" ]];then
  echo "Error: invalid fuzzer option for '--adapt_to': $adapt_to_opt"
  exit 1
fi

target_list_file=$5
if [[ -f "$target_list_file" ]];then
  echo "== found target list file, will only run from this list =="
  run_all=1
else
  echo "== target list file is not found; will run all from the constraint folder =="
  run_all=0
fi

# read the target file
unset lines

if [[ $run_all -eq 1 ]];then
  while IFS= read -r line;
  do
    lines+=("$line")
  done < "$target_list_file"
else
  lines=()
fi

containsElement () {
  local e match=$1
  shift
  for e;
  do
    if [[ "$e" == "$match" ]];then
       return 0
    fi
  done
  return 1
}

do_testing() {
  local package=$1
  local constrt_file=$2
  local workdir=$3
  local adapt_to_opt=$4

  args=(
    "$constrt_file"
    "${package}/${package}_dtypes.yml"
    "--max_iter=100"
    "--workdir=$workdir"
    "--consec_fail=4"
    "--cluster"
    "--verbose"
    "--dist_threshold=0.5"
    "--dist_metric=jaccard"
    "--adapt_to=$adapt_to_opt"
    "--fuzz_optional"
    "--gen_script"
  )

  if [ "$package" == "pytorch" ];then
    args+=("--data_construct=tensor")
  elif [ "$package" == "mxnet" ];then
    args+=("--data_construct=nd.array")
  fi

  if [ "$if_follow_constraints" == "follow" ];then
    args+=("--obey")
  fi

  python fuzzer/fuzzer-driver.py "${args[@]}"
}

constraints_files=("$constraints_folder"/*)
# shuffle
rand_constraints=$(printf '%s\n' "${constraints_files[@]}" | perl -MList::Util=shuffle -e 'print shuffle<STDIN>')

for c in ${rand_constraints[@]}; do
  name=$( basename "$c" )
  # NOTE: each filename in given list should be in form of xxx.yaml (without any dir prefix)
  containsElement "$name" "${lines[@]}"
  run_status=$?
  # skip the ones not in target list
  if [[ $run_status -eq 1 && $run_all -eq 1 ]];then
    continue
  fi

  if grep -q "$name" "$workorder_record"; then
    echo "Skipping $name"
    continue
  else
    echo "$name" >> "$workorder_record"
  fi

  workdir="$WORKDIR/${name}_workdir"
  mkdir -p "$workdir"
  do_testing "$package" "$c" "$workdir" "$adapt_to_opt"

  status=$?
  if [[ $status -eq 0 ]];then
    status_msg="ok"
  else
    status_msg="fail"
  fi
  echo "===  $( basename "$c" ) ===    $status_msg"
  echo "continue? [y/n]"
  read -r go_on
  if [[ "$go_on" == "y" ]]; then
    continue
  else  # anything other than 'y' will break
    break
  fi
done
