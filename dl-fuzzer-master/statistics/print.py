
import sys
import pickle
import re
import argparse
import numpy as np
    
def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret
        

def read_list(path):
    ret = read_file(path)
    return [x.replace('\n', '') for x in ret]

def print_data_shape(data):
    try:
        print(data.shape)
    except:
        print('value: '+str(data))

def detect_nan_inf(data):
    # detect if data contains nan or inf
    try:
        data = data.asnumpy()
    except:
        pass
    
    try:
        if np.isnan(data).any() or np.isinf(data).any():
            return True
        else:
            return False
    except:
        return False


def main(bash_path, list_arg, arg, model_input, shape, detect_nan):
    # bash_path: path to bash script
    # (Optional) arg: which arg to print, if None print all
    # (Optional) model_input: bool, whether to print model input
    # (Optional) shape: bool, whether to print the shape of the target parameter/model_input
    # (Optional) detect_nan: whether the target parameter contains nan
    content = read_list(bash_path)
    content  = [x.split('/')[-1][:-3] for x in content]
    if model_input:
        content = [x.split('_')[1] for x in content]
    else:
        content = [x.split('_')[0] for x in content]
    

    prefix = re.sub(r'(.*\/)[\w]+', r'\1', bash_path)
    #path_prefix = '/home/workdir/expect_ok_prev_ok/mxnet.ndarray.op.split.yaml_workdir/'
    for c in content:  
        data = pickle.load(open(prefix+c+'.p', 'rb'))
        print(prefix+c+'.p')
        if list_arg:
            print(data.keys())
        
        elif model_input:
            # print model input
            if detect_nan:
                print(detect_nan_inf(data))
            elif shape:
                print_data_shape(data)
            else:
                print(data)
        elif arg:
            if arg not in data:
                print("cannot find such argument\n")
                continue
            if detect_nan:
                print(detect_nan_inf(data[arg]))
            elif shape:
                print_data_shape(data[arg])
            else:
                print(data[arg])

        else:
            if detect_nan:
                for param in data:
                    print(param+': '+ str(detect_nan_inf(data[param])))
            else:
                print(data)

        print()




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('bash_path')
    parser.add_argument('--list_arg', default=False, action='store_true')
    parser.add_argument('--arg', default=None)
    parser.add_argument('--model_input', default=False, action='store_true')
    parser.add_argument('--shape', default=False, action='store_true')
    parser.add_argument('--detect_nan', default=False, action='store_true')
    
    args = parser.parse_args()


    
        
    main(args.bash_path, args.list_arg, args.arg, args.model_input, args.shape, args.detect_nan)