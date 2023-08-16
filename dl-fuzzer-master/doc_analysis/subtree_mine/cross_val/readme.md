8-2 division

min_support: 5, 10, 15, 20
min_conf: 0.9, 0.8, 0.7, ...
topK: -1, 2, 4, 6, 8, 10


1. `divide_data.py`

break the data into `num_fold` (=5) chucks and stores the sentence indices of each chuck into `./chuck_5/xx_chuck.yaml`

2. `parse_mine.py`

Parse the sentence of each chuck using dependency parser and mine the chucks with each min_support. Store the mining input, mining output, and parsed result into `./mining_data/tf/xxx`


3. `build_mapping.py`

Build Mapping (subtree to IRs) for each combination of `min_supp`, `min_conf`, `top_k`, `i` (fold). Store the mapping into `./rule/tf/xxx.yaml`, and log in `./rule/tf_log`

4. `eval.py`

Calculate the precision/recall/F1-score/accuracy for the IR extracted by applying the mapping obtained using `build_mapping.py`. Store the result in `./result/tf.csv`