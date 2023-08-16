import os
import pandas as pd
import sys
sys.path.insert(0,'../')
import prepare_data
from nltk.parse.corenlp import CoreNLPDependencyParser
import parse_mine_result
from util import *
import argparse

# given min_supp and label, get mining result for 5fold dataset 

def get_train_test_indices(chuck_data, test_chuck_idx):
    # return the row indices of training data and testing data
    
    training_indices = []
    for chuck_idx in chuck_data:
        assert len(list(set(chuck_data[chuck_idx]))) == len(chuck_data[chuck_idx])
        if chuck_idx == test_chuck_idx:
            continue
            
        training_indices += chuck_data[chuck_idx]
    return training_indices, chuck_data[test_chuck_idx]


def run(framework, label_path, chuck_record_path, word_map_path, inverse_word_map_path, save_path, treeminer_path, config_path):
    del_file(save_path, etd='*')
    config = read_yaml(config_path)
    num_fold = config['num_fold']
    label_df = pd.read_csv(label_path)
    chuck_record = read_yaml(chuck_record_path)
    word_map = read_yaml(word_map_path)
    # inverse_word_map = read_yaml(inverse_word_map_path)
    # for i in range num_fold 
    for i in range(num_fold):
        # fold#i, use chuck_i as test set
        print('Iter %s/%s' % (i+1, num_fold))
        # 1. prepare training data
        train_indices, test_indices = get_train_test_indices(chuck_record, i)
        print('Total: %s, Train: %s, Test: %s' % (len(label_df), len(train_indices), len(test_indices)))
        # 2.1 prepare training data
        assert len(list(set(train_indices))) == len(train_indices)
        sent_idx = prepare_data.get_sent_idx(label_df, train_indices, remove_noconstr_sent=True)  
        print('Selected %s sentences for mining from %s training samples.' %(len(sent_idx), len(train_indices))) 
        sent_set = prepare_data.prepare_sent(label_df, sent_idx, col='Normalized_descp', lower=True) 
        # 2.2 convert sent into trees
        parser = CoreNLPDependencyParser(url='http://localhost:9000')    
        dataset = prepare_data.prepare_mining_dataset(sent_set, word_map, parser)
        # print(dataset)
        train_idx_map = prepare_data.gen_idx_map(sent_idx)   # map from tree idx to sent idx
        
        for min_supp in config['min_support']:
            print('\tUsing min_support=%s' % min_supp)
            # 2.3 save mining input data
            mining_input_path = os.path.join(save_path, '%s-fold_minsupp_%s_mineinput_%s'%(num_fold, min_supp, i))
            save_list(dataset, mining_input_path)
            train_idx_map_path = os.path.join(save_path, '%s-fold_minsupp_%s_idxmap_%s'%(num_fold, min_supp, i))  
            save_yaml(train_idx_map_path, train_idx_map)
            for max_len in config['max_len']:
                mining_output_path =  os.path.join(save_path, '%s-fold_minsupp_%s_maxlen_%s_mineoutput_%s'%(num_fold, min_supp, max_len, i))
                # 3. call treeminer
                print('\tCalling treeminer...')
                call_tree_miner(treeminer_path, mining_input_path, mining_output_path, min_supp, max_len)
                
                
                # 4. parse treeminer output
                parsed_result_path = os.path.join(save_path, '%s-fold_minsupp_%s_maxlen_%s_parsedresult_%s.csv'%(num_fold, min_supp, max_len, i))
                parsed_mine_result = parse_mine_result.run(mining_output_path, inverse_word_map_path, train_idx_map_path, parsed_result_path)
                print('\tGet %s subtree'%len(parsed_mine_result))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('framework')
    parser.add_argument('label_path')
    parser.add_argument('chuck_record_path')
    parser.add_argument('word_map_path')
    parser.add_argument('inverse_word_map_path')
    parser.add_argument('save_path')
    parser.add_argument('--config_path', default='./config.yaml')
    parser.add_argument('--treeminer_path', default='../TreeMiner/treeminer')
    

    args = parser.parse_args()
    framework = args.framework
    label_path = args.label_path
    chuck_record_path = args.chuck_record_path
    word_map_path = args.word_map_path
    inverse_word_map_path = args.inverse_word_map_path
    treeminer_path = args.treeminer_path
    save_path = args.save_path
    config_path = args.config_path
    run(framework, label_path, chuck_record_path, word_map_path, inverse_word_map_path, save_path, treeminer_path, config_path)

# framework = 'tf'
# label_path = '../sample/tf_label.csv'
# chuck_record_path = './chuck_5/tf_chuck.yaml'
# word_map_path = '../tree_data/word_map'
# inverse_word_map_path = '../tree_data/inverse_word_map'
# treeminer_path = '../TreeMiner/treeminer'
# save_path = './mining_data/tf'
# num_fold = 5

# python parse_mine.py tf ../sample/tf_label.csv ./chuck_5/tf_chuck.yaml ../tree_data/word_map ../tree_data/inverse_word_map  ./mining_data/tf  > ./mining_data/tf/tf_log
