import sys
from os import walk
import re
import glob
import argparse
from utils import *



def main(workdir, title=None, csv_out=None):
    target_workdir = glob.glob('*_workdir')
    avg_rate = 0
    total_excp_cnt = 0
    total_inp_cnt = 0
    csv_lines = []
    csv_lines.append(['API', 'num_input', 'num_excp', 'excep_rate'])
    csv_lines.append(['total', 0, 0, 0])
    for tw in target_workdir:
        api = tw.replace('.yaml_workdir', '')
        exception_cnt = 0
        input_cnt = 0
        exception_cnt = len(glob.glob(tw+'/*.e'))
        input_cnt  = len(glob.glob(tw+'/*.p'))
        if input_cnt != 0:
            api_rate = exception_cnt/input_cnt
        else:
            api_rate = 0
        avg_rate+= api_rate
        total_excp_cnt += exception_cnt
        total_inp_cnt += input_cnt
        csv_lines.append([api, input_cnt, exception_cnt, api_rate])

    avg_rate = avg_rate/len(target_workdir)
    total_excp_rate = total_excp_cnt/total_inp_cnt
    csv_lines[1] = ['total', total_inp_cnt, total_excp_cnt, avg_rate]
    print('{}: \nExcep/Input: {}/{}\nTotal exception rate: {}, Average exception rate: {}'\
            .format(title, total_excp_cnt, total_inp_cnt, total_excp_rate, avg_rate))
    if csv_out:
        write_csv(csv_out, csv_lines)
    

if __name__== '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--workdir', type=check_dir_exist, required=True, help='Work directory that stores fuzzing output. E.g., /.../.workdir/expect_ok_permute')
    parser.add_argument('--title', required=False, default='Experiment', help='Optional: title of the experiment')
    parser.add_argument('--output', required=False, default=None, help='Optional: path to CSV file for statistics output. default: no output file')
    args = parser.parse_args()
    workdir = args.workdir
    title = args.title
    csv_out = args.output

    os.chdir(workdir)
    main(workdir, title, csv_out)


