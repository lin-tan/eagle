import sys
sys.path.insert(0,'..')

from extract_utils import *
import random 
import csv
import difflib

def get_intersection(l1,l2):
    ret = set.intersection(set(l1), set(l2))
    return list(ret)


def read_csv(path):
    # return a list which contains all rows
    ret = []
    with open(path) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            ret.append(row)

    return ret

def Diff_file(path1, path2):
    ret = []
    with open(path1, 'r') as hosts0:
        with open(path2, 'r') as hosts1:
            diff = difflib.unified_diff(
                hosts0.readlines(),
                hosts1.readlines(),
                fromfile='old',
                tofile='new',
            )
            for line in diff:
                ret.append(line)

    return ''.join(ret)


def main(path1, path2):
    files1 = get_file_list(path1)
    files2 = get_file_list(path2)
    intersection = get_intersection(files1, files2)

    for f in intersection:
        print(f)
        print(Diff_file(path1+f, path2+f))
        print()

if __name__ == "__main__":

    # print all the rows that is different 

    path1 = sys.argv[1]
    path2 = sys.argv[2]

    main(path1, path2)