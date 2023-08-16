#!/bin/bash

# prepare data, run the miner, build mapping, and extract constraints from the document

tf_min_support=10
pt_min_support=10
mx_min_support=20

tf_min_confidence=0.9
pt_min_confidence=0.7
mx_min_confidence=0.9

tf_max_iter=7
pt_max_iter=-1
mx_max_iter=-1


top_k=-1

framework=$1
# conda activate docter_fuzz
if [ $framework == "tf" ]; then
    python prepare_data.py ./sample/tf_label30.csv ./mining_data/tf/
    echo "Running TreeMiner"
    ./TreeMiner/treeminer -i ./mining_data/tf/mining_input -S $tf_min_support -m $tf_max_iter -o -l > ./mining_data/tf/mine_result
    python parse_mine_result.py ./mining_data/tf/mine_result  ./mining_data/tf/inverse_word_map ./mining_data/tf/train_idx_map  ./mining_data/tf/parsed_result.csv
    python train_fast.py ./mining_data/tf/parsed_result.csv ./sample/tf_label30.csv ./mining_data/tf/subtree_rule.yaml --min_conf=$tf_min_confidence  --top_k=$top_k
    python gen_constr_fast.py ../collect_doc/tf/tf21_all_src ./constr/tf/ ./mining_data/tf/subtree_rule.yaml ./config/tf_dtype_map.yaml
    python eval.py ./constr/tf/success/ ./eval/tf/


elif [ $framework == "pt" ]; then
    python prepare_data.py ./sample/pt_label30.csv ./mining_data/pt/ 
    echo "Running TreeMiner"
    ./TreeMiner/treeminer -i ./mining_data/pt/mining_input -S $pt_min_support -m $pt_max_iter -o -l > ./mining_data/pt/mine_result
    python parse_mine_result.py ./mining_data/pt/mine_result  ./mining_data/pt/inverse_word_map ./mining_data/pt/train_idx_map  ./mining_data/pt/parsed_result.csv
    python train_fast.py ./mining_data/pt/parsed_result.csv ./sample/pt_label30.csv ./mining_data/pt/subtree_rule.yaml --min_conf=$pt_min_confidence  --top_k=$top_k
    python gen_constr_fast.py ../collect_doc/pytorch/pt1.5_new_all/ ./constr/pt/ ./mining_data/pt/subtree_rule.yaml ./config/pt_dtype_map.yaml
    python eval.py ./constr/pt/success/ ./eval/pt/

elif [ $framework == "mx" ]; then
    python prepare_data.py ./sample/mx_label30.csv ./mining_data/mx/ 
    echo "Running TreeMiner"
    ./TreeMiner/treeminer -i ./mining_data/mx/mining_input -S $mx_min_support -m $mx_max_iter -o -l > ./mining_data/mx/mine_result
    python parse_mine_result.py ./mining_data/mx/mine_result  ./mining_data/mx/inverse_word_map ./mining_data/mx/train_idx_map  ./mining_data/mx/parsed_result.csv
    python train_fast.py ./mining_data/mx/parsed_result.csv ./sample/mx_label30.csv ./mining_data/mx/subtree_rule.yaml --min_conf=$mx_min_confidence  --top_k=$top_k
    python gen_constr_fast.py ../collect_doc/mxnet/mx1.6_new_all/ ./constr/mx/ ./mining_data/mx/subtree_rule.yaml ./config/mx_dtype_map.yaml
    python eval.py ./constr/mx/success/ ./eval/mx/

else
  echo "Error: unsupported framework choice: $package"
  exit 1

fi

# python gen_constr_fast.py ../collect_doc/sklearn/parsed/ ./generality_analysis/constr/all_on_sklearn ./mining_data/general/all_rule.yaml ./config/sk_dtype_map.yaml