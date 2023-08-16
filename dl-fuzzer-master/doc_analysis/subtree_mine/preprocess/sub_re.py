import sys
sys.path.insert(0,'..')
from util import * 
import argparse

p = r'`*((>|<|>\s*=|<\s*=)\s*([\w\.]+))`*'
annotation = ' REXPR'

def sub_re(src_text):
    anno_map = {}
    anno_map[annotation.strip()] = [x[0] for x in re.findall(p, src_text)]
    normalized_text = re.sub(p, annotation, src_text)
    # normalized_text = re.sub(r'\s+', ' ', normalized_text)

    # print(src_text)
    # print(normalized_text)
    # print(anno_map)
    # print()
    return remove_extra_space(normalized_text), anno_map

def test():
    test_case = {
        "An int scalar >= 0, <= beam_width (controls output size).": 'An int scalar RE_EXPR, REXPR (controls output size).',
        "currently only supports row and col dimension and should be >= 1.0": 'currently only supports row and col dimension and should be REXPR',
        "N-D `SparseTensor`, where `N >= 2`.": 'N-D `SparseTensor`, where `N REXPR`.',
        "An `int` that is `>= 1`.": 'An `int` that is REXPR.',
        "values >= num_buckets will cause a failure while values < 0 will be dropped.": "values REXPR will cause a failure while values REXPR will be dropped."
    }
    for s in test_case:
        normalized, _ = sub_re(s)
        if normalized==test_case[s]:
            print('PASS')
        else:
            print('FAIL')
            print('Original text: %s'% s)
            print('Normalized text: %s'% normalized)


if __name__ == '__main__':
    test()