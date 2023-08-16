import os
import random
import sys
sys.path.insert(0,'../')
from util import *

def sampling(src_folder, ratio, exclude=None):
    def _init_exclude_list(exclude_list):
        exclude_dict = {}
        for filename, argname, apiname in exclude_list:
            if filename in exclude_dict:
                exclude_dict[filename].append(argname)
            else:
                exclude_dict[filename] = [argname]
        return exclude_dict

    def _conver_sample_dict(sample_list):
        sample_dict = {}
        for filename, argname in sample_list:
            if filename in sample_dict:
                sample_dict[filename].append(argname)
            else:
                sample_dict[filename] = [argname]
        return sample_dict
    
    src_files = get_file_list(src_folder)

    if exclude:
        exclude_list = read_yaml(exclude)
        exclude_dict = _init_exclude_list(exclude_list)
    else:
        exclude_dict = {}
    
    sample_candidate = []
    cnt = 0
    for f in src_files:
        data = read_yaml(os.path.join(src_folder,f))
        for arg in data['constraints']:
            cnt += 1
            if arg in exclude_dict.get(f, []):
                continue
            sample_candidate.append([f, arg])
    
    sample_size = int(ratio*cnt)
    sample_list = random.sample(sample_candidate, sample_size)
    assert sample_size==len(sample_list)
    print('Sampled %s from %s parameters. ' %(sample_size, cnt))
    return _conver_sample_dict(sample_list)


def sample_data_init(data, arglist):
    label_data = {'title': data['title'],'constraints': {}}
    for arg in arglist:
        label_data['constraints'][arg] = data['constraints'][arg]
    return label_data

def main(src_folder, ratio, save_folder, exclude=None, label_folder=None, ):
    # exclude: a list of element [filename, argname, api_title], e.g. '../sample/tf_list'
    del_file(save_folder)
    sample_dict = sampling(src_folder, ratio, exclude)  # list of [filename, argname]
    label_file_list = get_file_list(label_folder) if label_folder else []
    for f in sample_dict:
        original_data = read_yaml(os.path.join(src_folder,f))
        
        if f in label_file_list:
            label_data = read_yaml(os.path.join(label_folder,f))
            sample_data = sample_data_init(label_data, sample_dict[f])
        else:
            sample_data = sample_data_init(original_data, sample_dict[f])
        save_yaml(os.path.join(save_folder, f), sample_data)

    save_yaml(os.path.join(save_folder, 'sample_list'), sample_dict)


# main(src_folder='../../collect_doc/tf/tf21_all_src/', ratio=0.05, save_folder='./tf/', exclude='../sample/tf_list', label_folder='../../extract_constraint/tf/tf21_all/changed/')
# # Sampled 190 from 3819 parameters.
# main(src_folder='../../collect_doc/pytorch/pt15_all_src/', ratio=0.05, save_folder='./pt/', exclude='../sample/pt_list', label_folder='../../extract_constraint/pytorch/pt15_all/')
# # Sampled 93 from 1865 parameters.
# main(src_folder='../../collect_doc/mxnet/mx16_all_src/', ratio=0.05, save_folder='./mx/', exclude='../sample/mx_list', label_folder='../../extract_constraint/mxnet/mx16_all/')
# # Sampled 320 from 6401 parameters.