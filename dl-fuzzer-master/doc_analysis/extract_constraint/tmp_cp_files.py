from shutil import copyfile
import os
import random
# import sys
# sys.path.insert(0,'..')
from extract_utils import *


def get_module_name(title):
    # given tf.keras.layers.Conv2d -> tf.keras.layers
    # note: return lower case
    return '.'.join(title.lower().split('.')[:-1])


def update_version(folder, version):
    
    target_api = get_file_list(folder)
    for ta in target_api:
        data = read_yaml(folder+ta) 
        data['version'] = version
        save_yaml(folder+ta, data)

def del_file(dir_addr, etd = '*.yaml'):
    # delete recursively all files existing in the folder
    del_files = glob.glob(dir_addr+'**/'+etd, recursive=True)
    for df in del_files:
        try:
            os.remove(df)
        except:
            pass


def main(constr_folder):
    file_list = get_file_list(constr_folder)
    for fname in file_list:
        data = read_yaml(os.path.join(constr_folder, fname))
        assert data['version'] == '1.4.0'
        data['version'] = '1.5.0'
        save_yaml(os.path.join(constr_folder, fname), data)

main('/home/pham84/Desktop/dl-fuzzer/doc_analysis/collect_doc/pytorch/pt1.5_new_all/')
main('/home/pham84/Desktop/dl-fuzzer/doc_analysis/collect_doc/pytorch/pt1.5_nn_new/')
main('/home/pham84/Desktop/dl-fuzzer/doc_analysis/collect_doc/pytorch/pt1.5_new/')
main('/home/pham84/Desktop/dl-fuzzer/doc_analysis/subtree_mine/constr/pt/success/')
main('/home/pham84/Desktop/dl-fuzzer/doc_analysis/subtree_mine/constr/pt/fail/')

# src1 = './mxnet/mx16_all'
# src2 = '../collect_doc/mxnet/mx16_all_src/'
# dest = '../../tmp_bl_data/mxnet/'
# api1 = get_file_list(src1)
# for a in api1:
#     copyfile(os.path.join(src2, a), os.path.join(dest, a))

# src1 = './tf/tf21_all/'
# src2 = './tf/tf21_all_new/changed/'
# dest = './tmp_data/tf30_data/'

# api1 = get_file_list(src1)
# api2 = get_file_list(src2)


# for a in api2:
#     if a not in api1:
#         copyfile(os.path.join(src2, a), os.path.join(dest, a))

# src = '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/extract_constraint/mxnet/mx16_all'
# dest1 = '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/extract_constraint/mxnet/mx16_1'
# dest2 = '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/extract_constraint/mxnet/mx16_2'

# api = get_file_list(src)
# half = int(len(api)/2)

# for f in api[:half]:
#     copyfile(os.path.join(src, f), os.path.join(dest1, f))

# for f in api[half:]:
#     copyfile(os.path.join(src, f), os.path.join(dest2, f))


# src_path = '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/collect_doc/pytorch/pt1.7_parsed/'
# update_version(src_path, '1.7.0')

# src_path = './mxnet/mx16_all/'
# dest_path = './mxnet/sampled_mx16/'
# ratio=0.1

# all_api = get_file_list(src_path)
# sampled = random.choices(all_api, k=int(ratio*len(all_api)))
# for s in sampled:
#     copyfile(src_path+s, dest_path+s)




# layer_api_path = './tf/constraint_4/changed/'
# function_api_path = './tf/tf21_layer/changed/'
# dest = './tf/tf21_all/'
# layer_api_path = '../collect_doc/mxnet/mx1.6_nn_parsed/'
# function_api_path = '../collect_doc/mxnet/mx1.6_parsed/'
# dest = '../collect_doc/mxnet/mx16_all_src/'

# del_file(dest)
# function_api = get_file_list(function_api_path)
# for f in function_api:
#     copyfile(function_api_path+f, dest+f)

# for f in get_file_list(layer_api_path):
#     if f not in function_api:
#         copyfile(layer_api_path+f, dest+f)


# src_path = '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/extract_constraint/mxnet/constraint_2/changed/'
# dest = '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/extract_constraint/mxnet/mx16_layer/changed/'

# target_api = get_file_list(src_path)
# module_name = ['mxnet.ndarray.op', 'mxnet.ndarray']

# for ta in target_api:
#     if get_module_name(ta.replace('.yaml', '')).lower() in module_name:
#         # print(ta)
#         copyfile(src_path+ta, dest+ta)


# src_path = '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/collect_doc/mxnet/mx1.7_nn_parsed/'
# target_api = get_file_list(src_path)
# for ta in target_api:
#     title = ta.replace('.yaml', '').lower()
#     if title.startswith('mxnet.gluon.contrib'):
#         if get_module_name(title) not in ['mxnet.gluon.contrib.nn', 'mxnet.gluon.contrib.rnn']:
#             print(ta)
#             os.remove(src_path+ta)




