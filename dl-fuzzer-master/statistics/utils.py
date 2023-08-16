import argparse
import os 
import csv
import yaml
import re

def check_dir_exist(d):
    d = os.path.abspath(d)
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError("%s is not a valid work directory" % d)
    return d

def write_csv(path, lines):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        for l in lines:
            writer.writerow(l)
            
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


def save_yaml(path, data):
    with open(path, 'w') as yaml_file:
        yaml.dump(data, yaml_file)

def read_yaml(path):
    with open(path) as yml_file:
        ret = yaml.load(yml_file, Loader=yaml.FullLoader)
    return ret


def convert_default(val):

    # check bool
    bool_val = ['false', 'true']
    if str(val).lower() in bool_val:
        return {'val':str(val).replace("'",''), 'dtype':'bool', 'ndim': 0}
        
    
    if str(val) in  ['None', '_Null']:
        return {'val':'None', 'dtype':None, 'ndim': None}
    else:
        try:
            return {'val':int(val), 'dtype':'int', 'ndim': 0}
        except:
            pass
        
        try:
            return {'val':float(val), 'dtype':'float', 'ndim': 0}
        except:
            pass

        if len(str(val))>0 and str(val)[0] in ['(', '[']:
            ndim = len(re.findall(r'[\[\(]', str(val).split(',')[0]))
            return {'val':str(val), 'dtype':None, 'ndim': ndim}

        elif re.match(r'.*\..*', str(val))!=None or str(val).startswith('<'):
            return {'val':str(val), 'dtype':None, 'ndim': None}
        else:
            return {'val':str(val), 'dtype':'string', 'ndim': None}