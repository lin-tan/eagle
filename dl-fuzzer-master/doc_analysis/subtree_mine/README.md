1. `bash text_preprocess.sh`: do normalization and parsing of original text, store them in the yaml files in `./tf`, `./pt`, `./mx` folder

2. `python samply.py`: sample 10%(default) from all parameters and parse them into sentences. The data is stored in folder `./sample`
- `tf_list`: list of sampled API and parameters
- `tf_label.csv`: the csv contains labels extracted by rule-based approach, which requires manual check


3. `python prepare_data.py`: prepare input data for TreeMiner. 
- (1) get the dependency parsing tree of each sentences
- (2) convert the tree into horizontal format (dfs-based)
- (3) encode each word into integers and get the encoded horizontal tree
- (4) generate input data file for TreeMiner with the data format specified on the github
- (5) store the generated input data file in `./tree_data/tree_data`; word_map, inverse_word_map in the same folder.

4. `./treeminer -i tree_data -S 10 -o -l > mine_result`
First copy the input data file to the corresponding folder (`TreeMiner/TreeMiner`). Then run the command

5. `python parse_mine_result.py`
First copy the TreeMiner result (`mine_result`) into `./tree_data` folder. This python script parse the mining result and store the parsed result in `./tree_data/parsed_result.csv`, which containing the encoded/decoded subtree, the index of trees that contains the subtree. The index of the tree starts from 0, which should match the index of `./tree_data/tree_data`.


6. `train.py`
build mapping


7. `gen_constr.py`
Match document sentences with the mapping, and convert IR to the constraints. 