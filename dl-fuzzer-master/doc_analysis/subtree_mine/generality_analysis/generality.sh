#!/bin/bash


framework=$1            # the framework to test on

if [ $framework == "tf" ]; then
    python gen_constr_fast.py ../collect_doc/tf/tf21_all_src ./constr/pt_mx_on_tf/ ./mining_data/general/pt_mx_rule.yaml ./config/tf_dtype_map.yaml
    python eval.py ./constr/pt_mx_on_tf/success ./eval/tf/


elif [ $framework == "pt" ]; then
    python gen_constr_fast.py ../collect_doc/pytorch/pt1.5_new_all/ ./constr/tf_mx_on_pt/ ./mining_data/general/tf_mx_rule.yaml ./config/pt_dtype_map.yaml
    python eval.py ./constr/tf_mx_on_pt/success ./eval/pt/

elif [ $framework == "mx" ]; then
    python gen_constr_fast.py ../collect_doc/mxnet/mx1.6_new_all/ ./constr/tf_pt_on_mx/ ./mining_data/general/tf_pt_rule.yaml ./config/mx_dtype_map.yaml
    python eval.py ./constr/tf_pt_on_mx/success ./eval/mx/

else
  echo "Error: unsupported framework choice: $package"
  exit 1

fi
