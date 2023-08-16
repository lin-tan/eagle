
import sys
sys.path.insert(0,'../')
from util import *
import pandas as pd
import random
import os


def main(arg_list_path, src_path, save_path):
    arg_list = read_yaml(arg_list_path)
    filename = arg_list_path.split('/')[-1]
    result = []
    for fname, arg in arg_list:
        doc_data = read_yaml(os.path.join(src_path, fname))
        api_name = doc_data['title']
        result.append([fname, arg, api_name])
    save_yaml(os.path.join(save_path, filename), result)    # override

main('../sample/tf_list', '../normalized_doc/tf', '../sample/')
main('../sample/pt_list', '../normalized_doc/pt', '../sample/')
main('../sample/mx_list', '../normalized_doc/mx', '../sample/')

