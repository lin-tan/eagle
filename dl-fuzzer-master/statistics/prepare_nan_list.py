import os
import argparse
import re
import pickle
import numpy as np
import csv

def get_file_list(dir_addr):

    files = []
    for _,_, filenames in os.walk(dir_addr):
        files.extend(filenames)
        break

    if '.DS_Store' in files:
        files.remove('.DS_Store')

    return files


def read_file(path):
    with open(path) as file:
        ret = file.readlines()
    return ret

def load_pickle(fpath):
    return pickle.load(open(fpath, 'rb'))


def write_csv(path, lines):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        for l in lines:
            writer.writerow(l)

def check_boundary_case(value):

    # check for None, 0, empty list(size=0)
    def _check_none(val):
        return val is None

    def _convert_numpy(val):
        try:
            return val.asnumpy()    # work only for mxnet tensor
        except:
            pass

        try:
            return np.array(val)    # work for list, tuple, tensorflow/pytorch array
        except:
            pass
    
    def _check_empty(val_np):
        return val_np.size == 0

    def _check_zero(val_np):
        if val_np.dtype!=np.bool:
            if (val_np==0) is False:
                return False
            try:
                return (val_np==0).any()
            except:
                pass
                
        return False

    if _check_none(value):
        return 'None'
    
    val_np = _convert_numpy(value)
    if _check_empty(val_np):
        return 'empty'

    if _check_zero(val_np):
        return 'zero'

    return None

    

        




def main(workdir):
    bug_type = 'Nan'
    sub_dir = [f.path for f in os.scandir(workdir) if f.is_dir()]
    csv_content = []
    csv_content.append(['API', 'Type', 'Count', 'Input', 'Tips'])
    stop_arg = ['name']
    for d in sub_dir:
        api = d.split('/')[-1].replace('.yaml_workdir', '')
        if not os.path.exists(os.path.join(d, 'script_record')):
            print('Cannot find file '+str(os.path.join(d, 'script_record')))
            continue
        script_record = [x.split(',')[0] for x in read_file(os.path.join(d, 'script_record'))]
        bug_record_path = os.path.join(d, bug_type+'_record')
        bug_script_bug_record_path = os.path.join(d, bug_type+'_script_record')
        tag=None
        if os.path.exists(bug_script_bug_record_path):
            trigger_pickle_file =  [x.replace('\n', '').split('/')[-1] for x in read_file(bug_record_path)]
            for p_file in trigger_pickle_file:
                data = load_pickle(os.path.join(d, p_file))
                for arg in data:
                    if arg in stop_arg:
                        continue
                    tag = check_boundary_case(data[arg])
                    if tag:
                        break
                if tag:
                    csv_content.append([api, bug_type, str(len(trigger_pickle_file)), os.path.join(d, bug_script_bug_record_path), '{}: {}'.format(arg, tag)])
                    break
    # print(csv_content)
    save_dir = os.path.dirname(os.path.abspath(workdir))
    write_csv(os.path.join(save_dir, 'nan_bug_list'), csv_content)
        
    



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('workdir')
    args = parser.parse_args()


    
        
    main(args.workdir)