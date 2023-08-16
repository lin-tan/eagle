import os
import pandas as pd
import itertools
import argparse
import sys
sys.path.insert(0,'../')
from util import *
import train


def build_single_mapping(mine_result_path, label_path, save_path, min_conf, top_k=-1):
    train.build(mine_result_path, label_path, save_path, min_conf=min_conf, top_k=top_k)

def get_all_comb(num_fold, min_support_list, min_conf_list, max_len_list):
    a = [min_support_list, min_conf_list, max_len_list, list(range(num_fold))]
    all_comb = list(itertools.product(*a))
    return all_comb



def main(framework, label_path, mine_result_folder, save_dir, config_path):
    del_file(save_dir, etd='*')
    config = read_yaml(config_path)
    num_fold = config['num_fold']
    all_comb = get_all_comb(num_fold, config['min_support'], config['min_conf'], config['max_len'])
    for min_supp, min_conf, max_len, i in all_comb:
        parsed_result_path = os.path.join(mine_result_folder, '%s-fold_minsupp_%s_maxlen_%s_parsedresult_%s.csv'%(num_fold, min_supp, max_len, i))
        # parsed_result_df = pd.read_csv(parsed_result_path)
        save_path = os.path.join(save_dir, '%s-fold_minsupp_%s_minconf_%s_maxlen_%s_rule_%s.yaml'%(num_fold, min_supp, min_conf, max_len, i))
        print('Saving subtree rule with min_support=%s, min_confidence=%s, max_len=%s, fold#%s to %s'%(min_supp, min_conf, max_len, i, save_path))
        build_single_mapping(parsed_result_path, label_path, save_path, min_conf)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('framework')
    parser.add_argument('label_path')
    parser.add_argument('mine_result_folder')
    parser.add_argument('save_dir')
    parser.add_argument('--config_path', default='./config.yaml')
    

    args = parser.parse_args()
    framework = args.framework
    label_path = args.label_path
    mine_result_folder = args.mine_result_folder
    save_dir = args.save_dir
    config_path = args.config_path
    main(framework, label_path, mine_result_folder, save_dir, config_path)

# framework = 'tf'
# label_path = '../sample/tf_label.csv'
# mine_result_folder = './mining_data/tf/'
# save_dir = './rule/tf/'


# python build_mapping.py tf ../sample/tf_label.csv ./mining_data/tf/ ./rule/tf/ > ./rule/tf_log
