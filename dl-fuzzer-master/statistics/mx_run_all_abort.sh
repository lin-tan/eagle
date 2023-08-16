#!/bin/bash
# run all abort and save the stderr to corresponding file
# script_list: txt file of all bash script path  (a list of path formatting as "/home/workdir/...")
# out_dir: the dir to save the stderr
# e.g. bash mx_run_all_abort.sh ./script_list ./abort_out/

bash_path_list=$1
out_dir=$2
while IFS= read -r bash_path;
do
  IFS='/' read -ra ADDR <<< $bash_path
  echo ${ADDR[4]}

  while IFS= read -r line;
  do
    echo "==Test Start=="
    $line
  done < $bash_path  >$out_dir"/"${ADDR[4]}"_out"  2>&1
done < $bash_path_list

python mx_check_abort.py $out_dir > "./crash_abort"