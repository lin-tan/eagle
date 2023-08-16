import argparse
import os
from util import *


# def _reset_model_test(package, title, model_test):
#     if package=='tensorflow' and not util.get_module_name(title)=='tf.keras.layers':
#         return False
#     if package=='torch' and not util.get_module_name(title)=='torch.nn':
#         return False
#     if package=='mxnet' and util.get_module_name(title) not in ['mxnet.gluon.nn', 'mxnet.gluon.rnn', 'mxnet.gluon.contrib.nn', 'mxnet.gluon.contrib.rnn']:
#         return False

#     return model_test   # remain the same

# def _reset_check_nan(package, title, check_nan):
#     if package=='tensorflow' and not util.get_module_name(title)=='tf.nn':
#         return False
#     if package=='torch' and not util.get_module_name(title)=='torch.nn.functional':
#         return False
#     if package=='mxnet' and util.get_module_name(title) not in ['mxnet.ndarray.op', 'mxnet.ndarray']:
#         return False

def add_layerobj(data):
    # the API is a layer constructor, which returns a layer object
    # check the output for NaN errors
    data['layer_constructor'] = True        # requires layer input
    data['check_nan'] = True
    return data

def add_layerfunc(data):
    # the API is a layer function API, which conducts layer calculation
    # check the output for NaN errors
    data['check_nan'] = True
    return data

def process_tf(data, module_name):
    if module_name == 'tf.keras.layers':
        data = add_layerobj(data)
    if module_name == 'tf.nn':
        data = add_layerfunc(data)
    return data

def process_pt(data, module_name):
    if module_name == 'torch.nn':
        data = add_layerobj(data)
    if module_name == 'torch.nn.functional':
        data = add_layerfunc(data)
    return data 

def process_mx(data, module_name):
    if module_name in {'mxnet.gluon.nn', 'mxnet.gluon.rnn', 'mxnet.gluon.contrib.nn', 'mxnet.gluon.contrib.rnn'}:
        data = add_layerobj(data)
    if module_name in {'mxnet.ndarray.op', 'mxnet.ndarray'}:
        data = add_layerfunc(data)
    return data 

def process_sk(data, module_name):
    data = add_layerfunc(data)  # add check_nan
    return data
    
def main(constr_folder):
    files = get_file_list(constr_folder)
    for fname in files:
        fpath = os.path.join(constr_folder, fname)
        data = read_yaml(fpath)
        package = data['package']
        module_name = get_module_name(data['title'])
        if package == 'tensorflow':
            data = process_tf(data, module_name)
        elif package == 'torch':
            data = process_pt(data, module_name)
        elif package == 'mxnet':
            data = process_mx(data, module_name)
        elif package == 'sklearn':
            data = process_sk(data, module_name)
        else:
            print('package %s not supported' % package)
            return 
        save_yaml(fpath, data)



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('constr_folder')
    args = parser.parse_args()


    
        
    main(args.constr_folder)