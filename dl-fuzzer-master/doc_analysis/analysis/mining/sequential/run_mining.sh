#!/bin/bash


run_tf(){
    # Data Loaded, 5697 sentences from 949 files
    # Data Loaded, 3394 sentences from 949 files
    python sequential_mining.py tf 5 2 descp
    python sequential_mining.py tf 5 1 name
}

run_pytorch(){
    # Data Loaded, 2091 sentences from 415 files
    # Data Loaded, 1263 sentences from 415 files  (should be 1142)
    # Data Loaded, 1450 sentences from 415 files
    python sequential_mining.py pytorch 5 2 descp
    python sequential_mining.py pytorch 5 1 doc_dtype
    python sequential_mining.py pytorch 5 1 name
}

run_mxnet(){
    # Data Loaded, 5436 sentences from 959 files
    # Data Loaded, 8878 sentences from 959 files  (should be 4388)
    # Data Loaded, 5928 sentences from 959 files
    python sequential_mining.py mxnet 5 2 descp
    python sequential_mining.py mxnet 5 1 doc_dtype
    python sequential_mining.py mxnet 5 1 name

}


# 18.7k sentences 
# 10.7k names


# python ../generate_dtype_ls.py

if [ "$1" == "tf" ] 
then
    run_tf
elif [ "$1" == "pytorch" ] 
then
    run_pytorch
elif [ "$1" == "mxnet" ]
then
    run_mxnet
elif [ "$1" == "all" ]
then
    run_tf
    run_pytorch
    run_mxnet
fi
