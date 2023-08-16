#!/bin/bash
# this script should be run within the docker container for inspecting the API output

package=$1
if [ -z "$package" ]; then
  echo "Error: need to specify a package [tensorflow | torch | mxnet]"
  exit 1
elif [[ "$package" != "tensorflow" && "$package" != "torch" && "$package" != "mxnet" ]];then
  echo "Error: unsupported package choice: $package"
  exit 1
fi

divs_folder="$2"
cd "$divs_folder" || { echo "Failed to change directory"; exit 1; }

dump_folder="/dump"
divs_name=$( basename "$divs_folder" )
problem_record="$divs_folder/problem_record_$divs_name"
done_file="$divs_folder/done_file_$divs_name"
for f in *.py; do
  f=$( realpath "$f" )
  pushd "$dump_folder" > /dev/null || { echo "Failed to change directory"; exit 1; }
  if grep -q "$f" "$done_file"; then
    echo "Skipping $f"
    continue
  fi
  timeout 10s python "$f"
  rm -rf "$dump_folder/*"
  popd > /dev/null || { echo "Failed to change back directory"; exit 1; }
  if [ $? -eq 1 ];then
    echo "$f" >> "$problem_record"
  fi
  echo "$f" >> "$done_file"
done

