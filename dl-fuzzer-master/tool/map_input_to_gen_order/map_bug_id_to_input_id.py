import argparse
import os
import pandas as pd
import pickle

import parse_log_gen_order as logparser

result_folder_locations = {
    'tensorflow': ['/local1/m346kim/dl-fuzzing/expr/tensorflow', '/local1/y2647li/dl-fuzzing/expr/tensorflow'],
    'pytorch': ['/local1/m346kim/dl-fuzzing/expr/pytorch', '/local1/y2647li/dl-fuzzing/expr/pytorch'],
    'mxnet': ['/local1/m346kim/dl-fuzzing/expr/mxnet']
}


class BugId:
    def __init__(self, id):
        self.id = id
        self.expect_ok_order = None
        self.expect_except_order = None

    def __str__(self):
        print('BugID: %s' % self.id)
        print('== bug-triggering input generation order in expect_ok: ==')
        if self.expect_ok_order is None:
            print('None')
        else:
            orders = sorted(self.expect_ok_order.values())
            print(orders)
        print('== bug-triggering input generation order in expect_exception: ==')
        if self.expect_except_order is None:
            print('None')
        else:
            orders = sorted(self.expect_except_order.values())
            print(orders)
        return ''


def get_gen_order(out_log_path):
    mapping = logparser.main(out_log_path)  # this gives {input_id: input_path}
    # want {input_path: input_id}
    rev_mapping = {v: k for k, v in mapping.items()}
    return rev_mapping


def map_record_file(record_file):
    if not os.path.exists(record_file):
        print('Warning: file specified not exist: %s' % record_file)
        return {}
    api_res_folder = os.path.dirname(record_file)

    out_log = os.path.join(api_res_folder, 'out')
    if not os.path.exists(out_log):
        print('Warning: out log file not exist: %s' % out_log)
        return {}

    with open(record_file, 'r') as f:
        records = f.read().splitlines()
    mapping = get_gen_order(out_log)

    if not mapping:  # no mapping due to failed to generate anything
        return {}

    input_to_gen_id = {}
    for line in records:
        line = line[:-1]  # remove the trailing 'y'
        line = line.replace('python ', '')
        # want to get the generation order of this particular input
        input_gen_id = mapping.get(line)
        if input_gen_id is None:
            print('Warning: %s is not found in file %s' % (line, record_file))
            print(len(mapping.keys()))
        else:
            input_to_gen_id[line] = input_gen_id

    return input_to_gen_id


def is_expect_ok(record_file_path):
    if 'expect_ok' in record_file_path:
        return True
    elif 'expect_exception' in record_file_path:
        return False
    print('Error: invalid file %s' % record_file_path)
    exit(1)


def is_early_gen(order1, order2):
    order1_values = order1.values()
    order2_values = order2.values()
    if min(order1_values) < min(order2_values):
        return True
    return False


def get_record_file(loc_list, path):
    assert path != '', 'given empty path'
    record_file = ''
    for loc in loc_list:
        record_path = os.path.join(loc, path)
        if os.path.exists(record_path):
            assert record_file == '', 'trying: %s but %s' % (record_path, record_file)
            record_file = record_path
    return record_file


def map_bug_id_to_input_id(bug_id, loc, fpath):
    # loc is a list now
    assert isinstance(loc, list)
    onebug = BugId(bug_id)
    paths = fpath.split(';')  # both expect_ok and expect_exception could contain bug-triggering input
    for p in paths:
        p = p.replace(' ', '')
        record_file = get_record_file(loc, p.replace(':/home', ''))
        input_to_gen_id = map_record_file(record_file)
        if is_expect_ok(record_file):
            if onebug.expect_ok_order is not None:
                if is_early_gen(input_to_gen_id, onebug.expect_ok_order):
                    print('Warning: overwriting existing expect_ok generation order')
                else:
                    continue
            onebug.expect_ok_order = input_to_gen_id
        else:
            if onebug.expect_except_order is not None:
                if is_early_gen(input_to_gen_id, onebug.expect_except_order):
                    print('Warning: overwriting existing expect_ok generation order')
                else:
                    continue
            onebug.expect_except_order = input_to_gen_id
    print(onebug)
    return onebug


def parse_input(fpath, res_loc, package):
    assert os.path.exists(fpath)
    bug_id_prefix = {'tensorflow': 'TF-', 'pytorch': 'PT-', 'mxnet': 'MX-'}[package]
    data = pd.read_table(fpath)
    # only want the bug_id, symptom, API name column
    filtered_data = data.filter(items=['BugID', 'Fuzz Input', 'Symptom', 'API Signature'])
    # filter out the Null value in 'API Name' column
    filtered_data = filtered_data[~pd.isnull(filtered_data['API Signature'])]
    filtered_data = filtered_data[~pd.isnull(filtered_data['Fuzz Input'])]
    filtered_data = filtered_data[~pd.isnull(filtered_data['BugID'])]
    # get where the Fuzz Input located
    inputs_locations = filtered_data['Fuzz Input']
    bugids = list(filtered_data['BugID'])
    assert len(inputs_locations) == len(bugids)
    bugs_mappings = []  # will be a list of BugId objects
    for i, l in enumerate(inputs_locations):
        bug_id = bugids[i]
        onebug_mapping = map_bug_id_to_input_id(bug_id_prefix+str(int(bug_id)), res_loc, l)
        bugs_mappings.append(onebug_mapping)
    if package == 'tensorflow':
        pickle.dump(bugs_mappings, open('tf_mappings.p', 'wb'))
    elif package == 'pytorch':
        pickle.dump(bugs_mappings, open('pt_mappings.p', 'wb'))
    elif package == 'mxnet':
        pickle.dump(bugs_mappings, open('mx_mappings.p', 'wb'))
    return bugs_mappings


def caught_bug_by_count(input_gen_order, count):
    # check if any number in input_gen_order <= count
    if input_gen_order is None:
        return False
    for i in input_gen_order.values():
        if i <= count:
            return True
    return False


def split_ratio(mappings, ok_ratio, excpt_ratio, total):
    ok_count = int(ok_ratio * total)
    excpt_count = int(excpt_ratio * total)
    assert ok_count + excpt_count == total, 'ok_count:excpt_count=%d:%d' % (ok_count, excpt_count)

    bugs_caught = []
    uncaught_bugs = []
    bugs_caught_record = [False] * len(mappings)
    eo_caught = []
    ee_caught = []
    for i, bug in enumerate(mappings):
        assert isinstance(bug, BugId)
        if caught_bug_by_count(bug.expect_ok_order, ok_count) or \
           caught_bug_by_count(bug.expect_except_order, excpt_count):
            bugs_caught.append(bug)
            bugs_caught_record[i] = True
            if caught_bug_by_count(bug.expect_ok_order, ok_count):
                eo_caught.append(bug)
            if caught_bug_by_count(bug.expect_except_order, excpt_count):
                ee_caught.append(bug)

    print('After split, we catch %d bugs' % sum(bugs_caught_record))
    # report uncaught
    print('---- reporting uncaught bugs %s:%s----' % (ok_count, excpt_count))
    for i, caught in enumerate(bugs_caught_record):
        if not caught:
            print(mappings[i])
            uncaught_bugs.append(mappings[i])
    print('---- end uncaught bugs %s:%s----'% (ok_count, excpt_count))
    return sum(bugs_caught_record), uncaught_bugs, eo_caught, ee_caught


def mapper(bugs, package, ok_ratio, excpt_ratio, total_input):
    bugs_input_order_mappings = parse_input(bugs, result_folder_locations[package], package)
    #if package == 'tensorflow':
    #    bugs_input_order_mappings = pickle.load(open('tf_mappings.p', 'rb'))
    #elif package == 'pytorch':
    #    bugs_input_order_mappings = pickle.load(open('pt_mappings.p', 'rb'))
    #else:
    #    exit(1)

    assert isinstance(bugs_input_order_mappings, list)
    print('Before split, we catch %d bugs' % len(bugs_input_order_mappings))
    num_caught, uncaught_bugs, eo_list, ee_list = split_ratio(bugs_input_order_mappings, ok_ratio, excpt_ratio, total_input)
    return len(bugs_input_order_mappings), num_caught, uncaught_bugs, eo_list, ee_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bugs', type=str,
                        help='tsv file containing the unique bugs')
    parser.add_argument('package', type=str,
                        help='choice of [tensorflow|pytorch|mxnet]')
    parser.add_argument('ok_ratio', type=float,
                        help='ratio of input for expect_ok case;'
                             'should be in range [0,1]; ok_ratio + excpt_ratio = 1')
    parser.add_argument('excpt_ratio', type=float,
                        help='ratio of input for expect_exception case;'
                             'should be in range [0,1]; ok_ratio + excpt_ratio = 1')
    parser.add_argument('--total_input', type=int, default=1000,
                        help='number of total input for each case, default to be 1000')
    args = parser.parse_args()

    assert args.package in ['tensorflow', 'pytorch', 'mxnet']
    assert 0 <= args.ok_ratio <= 1
    assert 0 <= args.excpt_ratio <= 1
    assert args.ok_ratio + args.excpt_ratio == 1
    mapper(args.bugs, args.package, args.ok_ratio, args.excpt_ratio, args.total_input)

