import os
import random
import argparse
from util import *
import sys
# sys.path.insert(0,'../')
sys.path.insert(0,'./cross_val/')
from eval import Eval_Counter, is_ir_empty


cat_group = {
    'dtype': ['dtype'],
    'structure': ['structure', 'tensor_t'], 
    'shape': ['shape', 'ndim'],
    'validvalue': ['range', 'enum']
}


constr_cat = ['dtype', 'structure', 'tensor_t', 'shape', 'ndim', 'range', 'enum']


def init_constr():
    # sentence-level IR
    ret = {}
    for cat in constr_cat:
        ret[cat] = set()
    return ret

def get_constr(arg_data):
    constr_dict = init_constr()
    for cat in constr_cat:
        if cat in arg_data: 
            constr_dict[cat] = set(arg_data[cat])       # [IMPORTANT] convert to set
    return constr_dict


def main(extracted_folder, label_folder, ):
    eval_counter = Eval_Counter()
    eval_counter.reset()
    sample_list = read_yaml(os.path.join(label_folder, 'sample_list'))
    extracted_file_list = get_file_list(extracted_folder)
    for f in sample_list:
        label_data = read_yaml(os.path.join(label_folder, f))
        if f in extracted_file_list:
            extracted_data = read_yaml(os.path.join(extracted_folder,f))
        else: 
            extracted_data = {}


        for arg in sample_list[f]:
            label_constr = get_constr(label_data['constraints'][arg])
            if extracted_data:
                extracted_constr = get_constr(extracted_data['constraints'][arg]) 
            else:
                extracted_constr = init_constr()

            eval_counter.update(label_constr, extracted_constr)
    eval_counter.eval() 
    print('Precision')
    print(eval_counter.precision)
    print('Recall')
    print(eval_counter.recall)
    print('F1')
    print(eval_counter.f1)
    print('accuracy')
    print(eval_counter.accuracy)
    
# main(extracted_folder='../../extract_constraint/tf/tf21_all/changed/', label_folder='./tf/')

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('extracted_folder')
    parser.add_argument('label_folder')

    

    args = parser.parse_args()
    extracted_folder = args.extracted_folder
    label_folder = args.label_folder

    main(extracted_folder, label_folder)
