import sys
sys.path.insert(0,'..')

from extract_utils import *
import random 
import os 
from shutil import copyfile

def get_eval_cnt(eval_cnt, num_files):
    eval_cnt = convert_str2numeric(eval_cnt)
    if eval_cnt<1:
        return round(eval_cnt*num_files)
    else:
        return eval_cnt


def split_list(l):
    half = len(l)//2
    return l[:half], l[half:]

def main(framework, eval_cnt):
    file_list = read_list('./{}_list'.format(framework))
    eval_cnt = get_eval_cnt(eval_cnt, len(file_list))
    candidate = file_list[:eval_cnt]   

    # create dir
    create_dir('./{}/danning/'.format(framework), clean=True)
    # create_dir('./{}/mijung/'.format(framework), clean=True)
    # create_dir('./{}/yitong/'.format(framework), clean=True)

    # l1, l2 = split_list(candidate)

    for f in candidate:
        # f is the file path
        filename = f.split('/')[-1]
        copyfile(f, './{}/danning/{}'.format(framework, filename))
    #     copyfile(f, './{}/mijung/{}'.format(framework, filename))

    # for f in l2:
    #     filename = f.split('/')[-1]
    #     copyfile(f, './{}/danning/{}'.format(framework, filename))
    #     copyfile(f, './{}/yitong/{}'.format(framework, filename))





if __name__ == "__main__":

    framework = sys.argv[1]
    eval_cnt = sys.argv[2]

    main(framework, eval_cnt)