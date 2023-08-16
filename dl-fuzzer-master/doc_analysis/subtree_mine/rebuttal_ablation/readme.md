Turn off min_conf, keep min_supp the same

### Command for training: 


python train_fast.py ./mining_data/tf/parsed_result.csv ./sample/tf_label30.csv ./rebuttal_ablation/rules/tf_subtree_rule.yaml --min_conf=0  --top_k=-1

python train_fast.py ./mining_data/pt/parsed_result.csv ./sample/pt_label30.csv ./rebuttal_ablation/rules/pt_subtree_rule.yaml --min_conf=0  --top_k=-1

python train_fast.py ./mining_data/mx/parsed_result.csv ./sample/mx_label30.csv ./rebuttal_ablation/rules/mx_subtree_rule.yaml --min_conf=0  --top_k=-1


 ( there are empty subtrees that without constr mathced because we do the annotation filtering. Function `filter_constr_by_anno`)
tf: 
865 subtree mined in total, 767 subtree rule, 98 subtree without constr
Duration: 4.854465484619141 seconds

426 subtree mined in total, 424 subtree rule, 2 subtree without constr
Duration: 1.8271453380584717 seconds


321 subtree mined in total, 314 subtree rule, 7 subtree without constr
Duration: 2.9420084953308105 seconds





### Command for extraction
python gen_constr_fast.py ../collect_doc/tf/tf21_all_src ./rebuttal_ablation/constr/tf/ ./rebuttal_ablation/rules/tf_subtree_rule.yaml ./config/tf_dtype_map.yaml

python gen_constr_fast.py ../collect_doc/pytorch/pt1.5_new_all/ ./rebuttal_ablation/constr/pt/ ./rebuttal_ablation/rules/pt_subtree_rule.yaml ./config/pt_dtype_map.yaml

python gen_constr_fast.py ../collect_doc/mxnet/mx1.6_new_all/ ./rebuttal_ablation/constr/mx/ ./rebuttal_ablation/rules/mx_subtree_rule.yaml ./config/mx_dtype_map.yaml


Duratino: 1333.5877108573914 seconds

Number of files: 950
Constraint Count:
{'dtype': 3290, 'tensor_t': 1873, 'structure': 486, 'shape': 2540, 'ndim': 3261, 'enum': 1249, 'range': 2724, 'total': 15423}
Grouped result:
{'dtype': 3290, 'structure': 2133, 'shape': 3262, 'validvalue': 2823, 'total': 11508}
Constraints min: 1 max: 74 (tf.keras.layers.gru.yaml) avg: 12.113684210526316




Duratino: 327.4605128765106 seconds  + 91

Number of files: 498
Constraint Count:
{'dtype': 1644, 'tensor_t': 720, 'structure': 264, 'shape': 747, 'ndim': 1559, 'enum': 78, 'range': 1160, 'total': 6172}
Grouped result:
{'dtype': 1644, 'structure': 891, 'shape': 1559, 'validvalue': 1199, 'total': 5293}
Constraints min: 1 max: 49 (torch.onnx.export.yaml) avg: 10.6285140562249



Duratino: 497.3304386138916 seconds +11


Number of files: 1009
Constraint Count:
{'dtype': 3741, 'tensor_t': 94, 'structure': 2717, 'shape': 211, 'ndim': 3639, 'enum': 275, 'range': 2999, 'total': 13676}
Grouped result:
{'dtype': 3741, 'structure': 2731, 'shape': 3639, 'validvalue': 3172, 'total': 13283}
Constraints min: 1 max: 185 (mxnet.io.imagedetrecorditer.yaml) avg: 13.164519326065411





### Command for eval

python eval.py ./rebuttal_ablation/constr/tf/success/ ./eval/tf/
python eval.py ./rebuttal_ablation/constr/pt/success/ ./eval/pt/
python eval.py ./rebuttal_ablation/constr/mx/success/ ./eval/mx/



(docter_fuzz) xdanning@deepgpu0:/local1/xdanning/docter/code/dl-fuzzer/doc_analysis/subtree_mine$ python eval.py ./rebuttal_ablation/constr/tf/success/ ./eval/tf/
Precision
{'dtype': 0.08176100628930817, 'structure': 0.7272727272727273, 'shape': 0.10256410256410256, 'validvalue': 0.050359712230215826, 'all': 0.1092436974789916}
Recall
{'dtype': 0.09558823529411764, 'structure': 0.9411764705882353, 'shape': 0.13793103448275862, 'validvalue': 0.15555555555555556, 'all': 0.16560509554140126}
F1
{'dtype': 0.08813559322033898, 'structure': 0.8205128205128205, 'shape': 0.11764705882352941, 'validvalue': 0.07608695652173914, 'all': 0.13164556962025314}
accuracy
0.06395348837209303
(docter_fuzz) xdanning@deepgpu0:/local1/xdanning/docter/code/dl-fuzzer/doc_analysis/subtree_mine$ python eval.py ./rebuttal_ablation/constr/pt/success/ ./eval/pt/

Precision
{'dtype': 0.2962962962962963, 'structure': 0.8571428571428571, 'shape': 0.16455696202531644, 'validvalue': 0.2, 'all': 0.2796610169491525}
Recall
{'dtype': 0.36923076923076925, 'structure': 0.9, 'shape': 0.24074074074074073, 'validvalue': 0.5238095238095238, 'all': 0.4125}
F1
{'dtype': 0.3287671232876712, 'structure': 0.8780487804878048, 'shape': 0.1954887218045113, 'validvalue': 0.2894736842105263, 'all': 0.33333333333333326}
accuracy
0.09195402298850575
(docter_fuzz) xdanning@deepgpu0:/local1/xdanning/docter/code/dl-fuzzer/doc_analysis/subtree_mine$ 
(docter_fuzz) xdanning@deepgpu0:/local1/xdanning/docter/code/dl-fuzzer/doc_analysis/subtree_mine$ python eval.py ./rebuttal_ablation/constr/mx/success/ ./eval/mx/

Precision
{'dtype': 0.20218579234972678, 'structure': 0.8955223880597015, 'shape': 0.09142857142857143, 'validvalue': 0.10067114093959731, 'all': 0.29329173166926675}
Recall
{'dtype': 0.2846153846153846, 'structure': 0.9836065573770492, 'shape': 0.18823529411764706, 'validvalue': 0.5, 'all': 0.5122615803814714}
F1
{'dtype': 0.2364217252396166, 'structure': 0.9375, 'shape': 0.12307692307692308, 'validvalue': 0.16759776536312848, 'all': 0.3730158730158731}
accuracy
0.2317596566523605














## Exp2:  turn off min_supp

### Command for tree miner:

 remember to delete the output file, otherwise it would fail when push
./TreeMiner/treeminer -i ./mining_data/tf/mining_input -S 1 -m 7 -o -l > ./rebuttal_ablation/mining_data/tf_mine_result_1

./TreeMiner/treeminer -i ./mining_data/pt/mining_input -S 1 -m 7 -o -l > ./rebuttal_ablation/mining_data/pt_mine_result_1

./TreeMiner/treeminer -i ./mining_data/mx/mining_input -S 1 -m 7 -o -l > ./rebuttal_ablation/mining_data/mx_mine_result_1

Timeing:
Fri Nov 12 13:14:33 EST 2021
Fri Nov 12 13:20:17 EST 2021
Fri Nov 12 13:28:39 EST 2021
mx stoped at 9:21PM



### command for parsing the minging result

python count_subtrees.py ./rebuttal_ablation/mining_data/tf_mine_result_1  


> 69225155

python count_subtrees.py ./rebuttal_ablation/mining_data/pt_mine_result_1  

> 92918041
python count_subtrees.py ./rebuttal_ablation/mining_data/mx_mine_result_1  

takes longer than 10h


### prepare mining result
python parse_mine_result.py ./rebuttal_ablation/mining_data/tf_mine_result_1  ./mining_data/tf/inverse_word_map ./mining_data/tf/train_idx_map  ./rebuttal_ablation/mining_data/tf_parsed_result.csv

> Sat Nov 13 17:52:21 EST 2021  
Sat Nov 13 18:14:32 EST 2021

<!-- python parse_mine_result.py ./mining_data/pt/mine_result  ./mining_data/pt/inverse_word_map ./mining_data/pt/train_idx_map  ./mining_data/pt/parsed_result.csv -->



### train 
python train_fast.py ./rebuttal_ablation/mining_data/tf_parsed_result.csv ./sample/tf_label30.csv ./rebuttal_ablation/mining_data/tf_subtree_rule.yaml --min_conf=0  --top_k=-1

    > Sat Nov 13 18:19:26 EST 2021
