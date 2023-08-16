
import sys
sys.path.insert(0,'../')
from util import *
import pandas as pd
import random
import os

def split_into_chucks(input_list, n, shuffle=True):
    if shuffle:
        random.shuffle(input_list)
    return [input_list[i::n] for i in range(n)]

def update_row_record(label_df, ):
    # return a dict mapping from API name and parameter name to row_indices
    row_idx_record = {}
    for index, row in label_df.iterrows():
        api = row['API']
        param = row['Arg']# .lower()
        if api not in row_idx_record:
            row_idx_record[api] = {}
        if param not in row_idx_record[api]:
            row_idx_record[api][param] = []
        row_idx_record[api][param].append(index)
    return row_idx_record

def main(arg_list_path, label_path, num_fold, save_path, framework):
    # label_path: path to the csv file
    arg_list = read_yaml(arg_list_path)
    label_df = pd.read_csv(label_path)
    row_idx_record = update_row_record(label_df)
    
    arg_chuck = split_into_chucks(arg_list, n=num_fold, shuffle=True)
    # print(len(arg_list))
    result = {} # chuck_id : row_idx
    all_param = set()
    for i, chuck in enumerate(arg_chuck):
        chuck_row_idx = []
        for fname, arg, api in chuck:
            api = api# .lower()
            arg = arg# .lower()
            if arg not in row_idx_record[api]:
                print(api)
                print(arg)
            assert len(set(row_idx_record[api][arg])) == len(row_idx_record[api][arg])
            if api+'__'+arg  in all_param:
                print(api+'__'+arg)
            assert api+'__'+arg not in all_param
            all_param.add(api+'__'+arg)
            chuck_row_idx += row_idx_record[api][arg]
        result[i] = chuck_row_idx
        # this_chuck = label_df.iloc[chuck_row_idx]
        # this_chuck.to_csv(os.path.join(save_path, '%s_chuck_%s.csv'%(framework, str(i))), index=False)
            
    save_yaml(os.path.join(save_path, '%s_chuck.yaml'%framework), result)

# main('../sample/tf_list', '../sample/tf_label30.csv', 5, './chuck30_5/', 'tf')
main('../sample/pt_list', '../sample/pt_label30.csv', 5, './chuck30_5/', 'pt')
main('../sample/mx_list', '../sample/mx_label30.csv', 5, './chuck30_5/', 'mx')

