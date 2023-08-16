"""
This script tries to collect the generated python scripts for each API under one lib
and convert the inputs to pytest compatible format to collect coverage / collect output
"""
import argparse
import os
import re
from multiprocessing import Pool

NUM_LINES_IN_INPUT_FILE = 4


def check_lib_choice(target):
    if target in ['tensorflow', 'pytorch', 'mxnet']:
        return target
    raise argparse.ArgumentTypeError("%s is not a valid target library choice" % target)


def collect_from_dir(target_name, directory, output_dir, n_cpu, purpose):
    dir_name_pattern = {'tensorflow': '^(tf\..*)\.yaml_workdir$',
                        'pytorch': '^(torch\..*)\.yaml_workdir$',
                        'mxnet': '^(mxnet\..*)\.yaml_workdir$',
                        }
    pattern = dir_name_pattern.get(target_name)
    assert pattern is not None

    # take a directory names and check if matches with the pattern
    directory = os.path.abspath(directory)

    worker_args = []
    for root, dirs, files in os.walk(directory):
        for d in dirs:
            signature = get_signature_from_dirname(d, pattern)
            dir_path = os.path.join(root, d)
            exclusion_list = get_exclusion_list(dir_path)
            if signature is not None:
                worker_args.append((dir_path, output_dir, signature, exclusion_list, purpose))
                # convert_to_tests(dir_path, output_dir, signature, exclusion_list)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with Pool(processes=n_cpu) as pool:
        pool.starmap(convert_to_tests, worker_args)


def get_exclusion_list(directory):
    exclusion_files = os.path.join(directory, 'timeout_record')
    if os.path.exists(exclusion_files):
        # need to treat input that cause timeout differently
        print('DEBUG: exclusion list exists')
        with open(exclusion_files, 'r') as f:
            exclusion_file_list = f.read().splitlines()
            # only take the last 2 tokens in the path string for each path
            # e.g., /home/workdir/expect_ok_prev_ok/tf.math.reduce_variance.yaml_workdir/9e051f70df5ae247174b0ad52d93fc9fb32cd290.p
            # will only take tf.math.reduce_variance.yaml_workdir/9e051f70df5ae247174b0ad52d93fc9fb32cd290.p
            res = set()
            for l in exclusion_file_list:
                exclusion_file_keyword = '/'.join(l.split('/')[-2:]) + 'y'
                res.add(exclusion_file_keyword)
            return res
    return set()


def get_signature_from_dirname(dname, pattern):
    m = re.match(pattern, dname)
    if not m:
        print('Skipping %s due to non-matching directory name' % dname)
        return None
    return m.group(1).replace('.', '_')  # need to replace '.' because pytest will get confused


def convert_to_tests(input_dir, output_dir, signature, exclusion_list, purpose, recursive=False):
    assert os.path.exists(input_dir)
    num_exclude = len(exclusion_list)  # used for sanity check
    excluded_count = 0  # used for sanity check

    for root, _, files in os.walk(input_dir):
        for fname in files:
            if not fname.endswith('.py'):  # only deal with .py files
                continue
            fpath = os.path.join(root, fname)
            fpath_keyword = '/'.join(fpath.split('/')[-2:])  # to keep consistent with the exclusion_list format
            if fpath_keyword in exclusion_list:
                excluded_count += 1
                print('-- excluding %s --' % fpath)
                continue
            print('++ converting %s ++' % fpath)
            outpath = os.path.join(output_dir, 'test_' + signature + '_' + fname)
            convert_each_to_test(fpath, outpath, purpose)
        if not recursive:
            break

    assert num_exclude == excluded_count, 'Sanity check failed (num_exclude vs. excluded_count): %d vs. %d' \
                                          % (num_exclude, excluded_count)  # sanity check


def get_lines_from_file(fpath):
    with open(fpath, 'r') as f:
        lines = f.read().splitlines()

    # all the generated input python scripts are in format:
    ## import pickle
    ## import <DL_lib>
    ## data = pickle.load(...)
    ## <API_func>(data)
    if len(lines) != NUM_LINES_IN_INPUT_FILE:
        print('## Skipping %s as it does not conform to the expected format' % fpath)
        return None

    # further sanity check
    if lines[0] != 'import pickle':
        print('## Skipping %s as it does not conform to the expected format' % fpath)
        return None

    return lines


def convert_each_to_test(fpath, outpath, purpose):
    lines = get_lines_from_file(fpath)
    if lines is None:
        return

    func_invok_line = lines[-1]
    lines = lines[:-1]

    func_invok_line = 'res = ' + func_invok_line
    # replace the function invocation to be a test function
    new_lines = ['def test():', ' ' * 4 + func_invok_line]
    lines += new_lines

    if purpose == 'res':
        # add 'import numpy as np' at the beginning
        lines = ['import numpy as np'] + lines
        new_lines = [' ' * 4 + 'if not np.isfinite(res).all(): exit(1)', 'try:',
                     ' ' * 4 + 'test()', 'except Exception:', ' ' * 4 + 'exit(0)']
        lines += new_lines

    with open(outpath, 'w+') as outf:
        outf.write('\n'.join(lines))
        outf.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=check_lib_choice,
                        help='target library within choice [tensorflow|pytorch|mxnet]')
    parser.add_argument('dir', type=str,
                        help='directory that contains results for each API')
    parser.add_argument('output', type=str,
                        help='output directory to store the converted files; will create if not exist')
    parser.add_argument('--ncpu', type=int, default=4,
                        help='number of cpus to do the conversion')
    parser.add_argument('--purpose', type=str, default='cov',
                        help='purpose of the conversion, choice within [cov|res]; if selected "cov",'
                             'the coversion is for coverage collection only; if selected "res",'
                             'the coversion is for collecting the results of each test')
    args = parser.parse_args()

    assert 0 < args.ncpu <= os.cpu_count()
    assert args.purpose in ['cov', 'res'], 'invalid choice for --purpose'

    collect_from_dir(args.target, args.dir, args.output, args.ncpu, args.purpose)


if __name__ == '__main__':
    main()
