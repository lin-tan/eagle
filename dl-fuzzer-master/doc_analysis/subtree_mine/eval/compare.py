import pandas as pd
import os
import random
import sys
sys.path.insert(0,'../')
from util import *

constr_cat = ['dtype', 'structure', 'tensor_t', 'shape', 'ndim', 'range', 'enum']

def init_constr_dict():
    ret = {}
    for cat in constr_cat:
        ret[cat] = []
    return ret

def read_constr(arg_data):
    constr = init_constr_dict()
    for cat in constr_cat:
        constr[cat] = arg_data.get(cat, [])
    return constr

def main(constr_folder, label_folder, save_path, sample=1):
    constr_files = get_file_list(constr_folder)
    label_files = get_file_list(label_folder)
    csv_title = [['API', 'Arg', 'Descp', 'default', 'doc_dtype', 'Catrgory', 'Label', 'Extracted']]
    diff = []
    for fname in label_files:
        if fname == 'sample_list':
            continue
        label_data = read_yaml(os.path.join(label_folder, fname))
        if fname in constr_files:
            constr_data = read_yaml(os.path.join(constr_folder, fname))
            for arg in label_data['constraints']:
                label_arg_data = label_data['constraints'][arg]
                arg_data = constr_data['constraints'][arg]

                label_constr = read_constr(label_arg_data)
                data_constr = read_constr(arg_data)
                for cat in constr_cat:
                    if set(data_constr[cat]) != set(label_constr[cat]):
                        diff.append([label_data['title'], arg, label_arg_data['descp'], str(label_arg_data.get('default', '')), str(label_arg_data.get('doc_dtype', '')), cat, str(label_constr[cat]), str(data_constr[cat])])

                
        else:
            for arg in label_data['constraints']:
                label_arg_data = label_data['constraints'][arg]
                label_constr = read_constr(label_arg_data)
                for cat in constr_cat:
                    if label_constr[cat]:
                        diff.append([label_data['title'], arg, label_arg_data['descp'], str(label_arg_data.get('doc_dtype', '')), cat, str(label_constr[cat]), ''])

    if sample!=1:
        diff = random.sample(diff, int(sample*len(diff)))
    write_csv(save_path, csv_title+diff)

main('../constr/tf/success/', './tf/', './tf_diff.csv')
main('../constr/pt/success/', './pt/', './pt_diff.csv')
main('../constr/mx/success/', './mx/', './mx_diff.csv')

main('../constr/tf/success/', './tf/', './tf_diff_sample.csv', 0.1)
main('../constr/pt/success/', './pt/', './pt_diff_sample.csv', 0.1)
main('../constr/mx/success/', './mx/', './mx_diff_sample.csv', 0.1)