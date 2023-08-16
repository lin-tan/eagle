#!/bin/bash

python ../generate_dtype_ls.py

# pytorch 2091 sentences
python frequent_itemset_mining.py pytorch apriori 0.01 2
python frequent_itemset_mining.py pytorch apriori 0.005 2  
python frequent_itemset_mining.py pytorch fmax 0.01 2
python frequent_itemset_mining.py pytorch fmax 0.001 2 

python frequent_itemset_mining.py tf apriori 0.01 2
python frequent_itemset_mining.py tf apriori 0.005 2  
python frequent_itemset_mining.py tf fmax 0.01 2
python frequent_itemset_mining.py tf fmax 0.001 2 