#!/bin/bash
LIB=${1}
VER=${2}

now="$(date +"%y_%m_%d_%H_%M_%S")"
LOG_FILE="/mnt/equivalentmodels_data/logs/generating_$LIB_$VER_$now.log"

exec &>$LOG_FILE

python generate_all_input.py $LIB $VER