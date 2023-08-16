#!/bin/bash
LIB=${1}
VER=${2}

now="$(date +"%y_%m_%d_%H_%M_%S")"
LOG_FILE="/mnt/equivalentmodels_data/logs/testing_${LIB}_${VER}_$now.log"

exec &>$LOG_FILE

python execute_testing_rules_multi.py $LIB $VER