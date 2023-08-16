import argparse
import os
import re


def match_order_start_line(l):
    m = re.match('#* ([0-9].*)/[0-9].* begin #*', l)
    if m:
        return int(m.group(1))
    return -1


def match_order_end_line(l):
    m = re.match('#* ([0-9].*)/[0-9].* done #*', l)
    if m:
        return int(m.group(1))
    return -1


def match_save_file(l):
    m = re.match('Saving seed to file ([a-zA-Z0-9_/.].*) ', l)
    if m:
        return m.group(1)


def parse_log(fpath):
    assert os.path.exists(fpath), '%s not exist' % fpath
    with open(fpath, 'r') as f:
        lines = f.read().splitlines()

    all_iteration_contents = dict()  # add the [] for index 0 as placeholder
    current_lines = []
    current_index = -1
    for l in lines:
        # Check for iteration begin
        idx = match_order_start_line(l)
        if idx > 0:
            # start work-around when where's no end line #
            if current_index > 0:
                all_iteration_contents[current_index] = current_lines
                current_lines = []
            # end work-around when where's no end line #
            current_index = idx
            continue

        # Check for iteration end
        idx = match_order_end_line(l)
        if idx > 0:
            all_iteration_contents[current_index] = current_lines
            current_index = -1
            current_lines = []
            continue

        if current_index > 0:
            current_lines.append(l)

    if len(all_iteration_contents) != 1000:
        print('Warning: fuzzer failed to generate input or other issue %s ' % fpath)
    return all_iteration_contents


# def parse_iteration_content(all_iteration_content,outputfile):
#     f = open(outputfile, "w")
#     f.write('Iter,path\n')
#     for i, lines in all_iteration_content.items():
#         for line in lines:
#             path = match_save_file(line)
#             if path:
#                 f.write('%s,%s\n' % (i, path))
#                 break
#     f.close()

# unable to save to file without major change, so just return the mapping
def parse_iteration_content(all_iteration_content):
    mapping = {}
    for i, lines in all_iteration_content.items():
        for line in lines:
            path = match_save_file(line)
            if path:
                mapping[i] = path
                break
    return mapping


def main(logfile):
    all_iteration_content = parse_log(logfile)
    return parse_iteration_content(all_iteration_content)


if __name__ == '__main__':
    # want to have a mapping
    # 1 : input_path_1
    # 2 : input_path_2
    # ...
    # and then reverse
    # input_path_1 : 1
    # input_path_2 : 2

    parser = argparse.ArgumentParser()
    parser.add_argument('logfile', type=str,
                        help='an output log file')
    args = parser.parse_args()
    main(args.logfile)

