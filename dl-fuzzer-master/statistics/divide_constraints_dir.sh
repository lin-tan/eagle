#!/bin/bash

#usage: bash divide_constraints_dir.sh ../constraints/constraint_1/changed 5 
constraints_dir=$1
group_num=$2 #how many groups do you want to divide yaml files in  $constraints_dir into?

pushd $constraints_dir > /dev/null
numfiles=(*.yaml)
numfiles=${#numfiles[@]}
group_size=$(echo $((numfiles / group_num + 1)))
echo "Total $numfiles yaml files to be divided into $group_num groups. $group_size yaml files in each division"

group_counter=1
new_dir_name=division_"${group_counter}"
mkdir -p $new_dir_name 
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
